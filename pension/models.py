from django.db import models
from users.models import User as users

# Create your models here.
class Pension(models.Model):     
    name = models.CharField(max_length=100)
    payBill_number = models.CharField(max_length=20)
    status = models.CharField(max_length=20)  
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True)  

    def __str__(self):
        return self.name

class PensionAccount(models.Model):  
    member = models.ForeignKey(users, on_delete=models.CASCADE ,limit_choices_to={'user_type': 'MANAGER'})
    total_pension_amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_opted_in = models.BooleanField()
    contribution_percentage = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"PensionAccount {self.member}"
