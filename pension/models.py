from django.db import models
from users.models import User as users

class Pension(models.Model):    
    STATUS_CHOICES = ['active', 'inactive'] 
    name = models.CharField(max_length=100)
    payBill_number = models.CharField(max_length=20)
    status = models.CharField(max_length=20, choices=[(status, status) for status in STATUS_CHOICES])  
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True)  

    def __str__(self):
        return self.name


class PensionAccount(models.Model):  
    member = models.ForeignKey(
        users, 
        on_delete=models.CASCADE,
        limit_choices_to={'user_type': 'MEMBER'}
    )
    total_pension_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    is_opted_in = models.BooleanField(default=False)
    contribution_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"PensionAccount {self.member}"

    def get_pension_amount(self, savings_amount):       
        if not self.is_opted_in:
            return 0.00
        return round(savings_amount * self.contribution_percentage, 2)