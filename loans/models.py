from django.db import models
from django.utils import timezone
from users.models import User  

class LoanAccount(models.Model):
    loan_type_choices = [
        ('emergency', 'Emergency'),
        ('personal', 'Personal'),
        ('business', 'Business'),
    ]
    loan_id = models.AutoField(primary_key=True)
    member = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='loans') 
    manager = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True, related_name='managed_loans') 
    requested_amount = models.DecimalField(max_digits=10, decimal_places=2)
    loan_status = models.CharField(max_length=20, choices=[
        ('Pending', 'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected')
    ])
    loan_type = models.CharField(max_length=20, choices=loan_type_choices, default='personal')
    loan_reason = models.CharField(max_length=255, blank=True, null=True, help_text='If emergency, specify reason (e.g., urgent medical bill for a family member)')
    
    total_loan_repaid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    timeline_months = models.IntegerField()
    requested_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    disbursed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Loan {self.loan_id}"

class Guarantor(models.Model):
    guarantor_id = models.AutoField(primary_key=True)
    loan = models.ForeignKey('LoanAccount', on_delete=models.CASCADE, related_name='guarantors')
    member = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='guaranteed_loans') 
    guarantor_name = models.CharField(max_length=100)
    guarantor_phone_number = models.CharField(max_length=20)
    status = models.CharField(max_length=10, choices=[
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('Pending', 'Pending')
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    responded_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Guarantor {self.guarantor_name}"

class LoanRepayment(models.Model):
    repayment_id = models.AutoField(primary_key=True)
    loan = models.ForeignKey('LoanAccount', on_delete=models.CASCADE, related_name='repayments')
    loan_amount_repaid = models.DecimalField(max_digits=10, decimal_places=2)
    loan_repayment_status = models.CharField(max_length=10, choices=[
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Overdue', 'Overdue')
    ])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Repayment {self.repayment_id}"

    

def __str__(self):
    return f"Repayment {self.loan_repayment_id} - Loan: {self.loan.loan_id} - Status: {self.status or 'N/A'}"

def repayment_status(self):
    if self.status == 'completed':
        return 'completed'
    if self.payment_date is None and self.amount_paid == 0:
        return 'pending'
    if self.payment_date:
        delay_days = (self.payment_date - self.due_date).days
    if delay_days <= 0:
        return 'pending' 
    if self.amount_remaining > 0 and delay_days > 0:
        return 'overdue'
        return 'pending'

def process_repayment_payment(self, amount):
    if amount <= 0:
        return False, "Payment amount must be positive.", amount

    amount_to_apply = min(amount, self.amount_remaining)
    self.amount_paid += amount_to_apply
    self.amount_remaining -= amount_to_apply

    if self.amount_remaining <= 0:
        self.amount_remaining = 0
        self.status = 'completed'
        self.payment_date = timezone.now()

    self.save()
    self.loan.process_payment(amount_to_apply)

    excess_payment = amount - amount_to_apply
    return True, "Payment processed.", excess_payment



    
 