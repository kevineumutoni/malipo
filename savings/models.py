from django.db import models
from django.utils import timezone
from users.models import User
from pension.models import PensionAccount
from transaction.models import Transaction
from transaction.daraja import DarajaAPI


class SavingsAccount(models.Model):
    member = models.ForeignKey(User, on_delete=models.CASCADE, related_name='savings_account')
    member_account_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    interest_incurred = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['member']

    def __str__(self):
        return f"{self.member.first_name}'s Savings: KES {self.member_account_balance}"


class SavingsContribution(models.Model):
    member = models.ForeignKey(User, on_delete=models.CASCADE, related_name='savings_contributions')
    saving = models.ForeignKey(SavingsAccount, on_delete=models.CASCADE, related_name='contributions')
    contributed_amount = models.DecimalField(max_digits=10, decimal_places=2)
    pension_percentage = models.DecimalField(max_digits=3, decimal_places=2)
    pension_amount = models.DecimalField(max_digits=10, decimal_places=2)
    vsla_amount = models.DecimalField(max_digits=10, decimal_places=2)
    transaction_id_c2b = models.ForeignKey(
        Transaction,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='c2b_contributions'
    )
    transaction_id_b2b = models.ForeignKey(
        Transaction,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='b2b_contributions'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Contribution for {self.saving.member.first_name}"

    def save(self, *args, **kwargs):
        if not self.pk:  # Only on create
            try:
                pension_account = PensionAccount.objects.get(member=self.member)
                self.pension_amount = pension_account.get_pension_amount(self.contributed_amount)
                self.pension_percentage = pension_account.contribution_percentage
                self.vsla_amount = self.contributed_amount - self.pension_amount
            except PensionAccount.DoesNotExist:
                self.pension_amount = 0.00
                self.pension_percentage = 0.00
                self.vsla_amount = self.contributed_amount

            # Update savings balance (VSLA portion)
            self.saving.member_account_balance += self.vsla_amount
            self.saving.save()

            # Handle pension allocation
            if self.pension_amount > 0:
                try:
                    pension_account = PensionAccount.objects.get(member=self.member)
                    provider = getattr(pension_account, 'provider', None)

                    if provider and provider.status == 'active':
                        # ✅ Initialize Daraja API
                        daraja = DarajaAPI()

                        # ✅ Use provider's PayBill number
                        b2b_response = daraja.b2b_payment(
                            receiver_shortcode=provider.payBill_number,
                            amount=self.pension_amount
                        )

                        # ✅ Create B2B Transaction — USING CORRECT FIELD NAMES
                        b2b_transaction = Transaction.objects.create(
                            member=self.member,
                            transaction_type='B2B',
                            amount_transacted=self.pension_amount,  # ✅ Was "amount" → now "amount_transacted"
                            payment_transaction_status='processing',  # ✅ Was "status" → now "payment_transaction_status"
                            provider=provider,  # ✅ Now exists in Transaction model
                            description=f"Pension contribution for {self.member.first_name}",  # ✅ Now exists
                            account_type='pension_contribution',  # ✅ Good to specify
                        )

                        self.transaction_id_b2b = b2b_transaction

                        # If Daraja accepted request
                        if isinstance(b2b_response, dict) and b2b_response.get('ConversationID'):
                            b2b_transaction.checkout_request_id = b2b_response.get('ConversationID')
                            b2b_transaction.save()
                        else:
                            # ✅ Update using correct field name
                            b2b_transaction.payment_transaction_status = 'failed'
                            b2b_transaction.save()
                            print("B2B Request Failed:", b2b_response)

                    else:
                        print(f"No active pension provider for {self.member.first_name}")
                except PensionAccount.DoesNotExist:
                    pass

            # Mark as completed
            self.completed_at = timezone.now()

        super().save(*args, **kwargs)