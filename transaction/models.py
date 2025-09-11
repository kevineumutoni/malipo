from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone

class Transaction(models.Model):
    TRANSACTION_TYPE_CHOICES = [
        ('C2B', 'Customer to Business'),
        ('B2C', 'Business to Customer'),
        ('B2B', 'Business to Business'),
    ]
    ACCOUNT_TYPE_CHOICES = [
        ('loan_repayment', 'Loan Repayment'),
        ('savings', 'Savings'),
        ('loan_disbursement', 'Loan Disbursement'),
    ]
    STATUS_CHOICES = [
        ('initiated', 'Initiated'),
        ('success', 'Success'),
        ('failed', 'Failed'),
        ('timeout', 'Timeout'),
        ('processing', 'Processing'),
    ]

    member = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='member_transactions',
        limit_choices_to={'user_type': 'MEMBER'}
    )
    manager = models.ForeignKey(
        'users.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='manager_transactions',
        limit_choices_to={'user_type': 'MANAGER'}
    )
    transaction_type = models.CharField(max_length=10, choices=TRANSACTION_TYPE_CHOICES)
    checkout_request_id = models.CharField(max_length=100, blank=True, null=True)
    account_reference = models.CharField(max_length=50, blank=True, null=True)
    amount_transacted = models.DecimalField(max_digits=10, decimal_places=2)
    paybill_number = models.CharField(max_length=30, blank=True)
    recipient_phone_number = models.CharField(max_length=20, blank=True)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPE_CHOICES)
    payment_transaction_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='initiated')
    callback_url = models.CharField(max_length=225, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    def clean(self):
        if self.account_type in ['savings', 'loan_repayment'] and not self.member:
            raise ValidationError("Member is required for savings or loan repayment.")
        if self.account_type == 'loan_disbursement' and not self.manager:
            raise ValidationError("Manager is required for loan disbursement.")

    def __str__(self):
        return f"Transaction {self.id} - {self.transaction_type} - {self.amount_transacted}"