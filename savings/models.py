from django.db import models
from django.conf import settings
from django.utils import timezone
from decimal import Decimal, InvalidOperation
from django.core.validators import MinValueValidator
from pension.models import PensionAccount
from transaction.models import Transaction
from transaction.daraja import DarajaAPI

class SavingsAccount(models.Model):
    member = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='savings_accounts' 
    )
    member_account_balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    interest_incurred = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['member']

    def __str__(self):
        return f"{self.member.first_name}'s Savings: KES {self.member_account_balance}"


class SavingsContribution(models.Model):
    member = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='savings_contributions' 
    )

    saving = models.ForeignKey(
        SavingsAccount,
        on_delete=models.CASCADE,
        related_name='contributions'
    )

    contributed_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    pension_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    vsla_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
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
    completed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Contribution for {self.member.first_name} ({self.member.national_id})"

    def save(self, *args, **kwargs):
        try:
            self.contributed_amount = Decimal(str(self.contributed_amount))
        except (InvalidOperation, ValueError, TypeError):
            raise ValueError("contributed_amount must be a valid number")

        if not self.pk:
            try:
                pension_account = PensionAccount.objects.get(member=self.member)
                self.pension_percentage = pension_account.contribution_percentage
                self.pension_amount = pension_account.get_pension_amount(self.contributed_amount)
            except PensionAccount.DoesNotExist:
                self.pension_percentage = Decimal('0.00')
                self.pension_amount = Decimal('0.00')

            self.vsla_amount = self.contributed_amount - self.pension_amount
            self.saving.member_account_balance += self.vsla_amount
            self.saving.save()

            if self.pension_amount > 0:
                try:
                    pension_account = PensionAccount.objects.get(member=self.member)
                    provider = pension_account.provider
                    if provider and provider.status == 'active':
                        daraja = DarajaAPI()
                        b2b_response = daraja.b2b_payment(
                            receiver_shortcode=provider.payBill_number,
                            amount=self.pension_amount
                        )

                        national_id = self.member.national_id or 'N/A'
                        description = f"Pension contribution for {self.member.first_name} (ID: {national_id})"

                        b2b_transaction = Transaction.objects.create(
                            member=self.member,
                            transaction_type='B2B',
                            amount_transacted=self.pension_amount,
                            payment_transaction_status='processing',
                            provider=provider,
                            description=description,
                            account_type='pension_contribution',
                        )

                        if isinstance(b2b_response, dict) and b2b_response.get('ConversationID'):
                            b2b_transaction.checkout_request_id = b2b_response['ConversationID']
                        else:
                            b2b_transaction.payment_transaction_status = 'failed'

                        b2b_transaction.save()
                        self.transaction_id_b2b = b2b_transaction

                except Exception:
                    pass

            self.completed_at = timezone.now()

        super().save(*args, **kwargs)