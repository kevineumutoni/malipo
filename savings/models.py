from django.db import models
from users.models import User
from transaction.models import Transaction


class SavingsAccount(models.Model):
    member = models.ForeignKey(User, on_delete=models.CASCADE, related_name='savings_account')
    member_account_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    interest_incurred = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.member.first_name}'s Savings: KES {self.member_account_balance}"


class SavingsContribution(models.Model):
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