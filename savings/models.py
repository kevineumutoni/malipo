from django.db import models
from users.models import User
from users.models import Member 



class Member(models.Model):
   member_id = models.CharField(max_length=10, primary_key=True)
 


# class PaymentTransaction(models.Model):
#     transaction_id = models.CharField(max_length=10, primary_key=True)f



class SavingsAccount(models.Model):
   saving_id = models.CharField(max_length=10, primary_key=True)
   member = models.ForeignKey(Member, on_delete=models.CASCADE)
   member_account_balance = models.DecimalField(max_digits=10, decimal_places=2)
   interest_incurred = models.DecimalField(max_digits=10, decimal_places=2)
   created_at = models.DateTimeField(auto_now_add=True)
   updated_at = models.DateTimeField(auto_now=True)


   def __str__(self):
       return f"SavingsAccount {self.saving_id}"


class SavingsContribution(models.Model):
   contribution_id = models.CharField(max_length=10, primary_key=True)
   saving = models.ForeignKey(SavingsAccount, on_delete=models.CASCADE)
   contributed_amount = models.DecimalField(max_digits=10, decimal_places=2)
   pension_percentage = models.DecimalField(max_digits=3, decimal_places=2)
   pension_amount = models.DecimalField(max_digits=10, decimal_places=2)
   vsla_amount = models.DecimalField(max_digits=10, decimal_places=2)
   # transaction_id_c2b = models.ForeignKey(
   #     PaymentTransaction, on_delete=models.SET_NULL,
   #     blank=True, null=True, related_name='contributions_c2b'
   # )
   # transaction_id_b2b = models.ForeignKey(
   #     PaymentTransaction, on_delete=models.SET_NULL,
   #     blank=True, null=True, related_name='contributions_b2b'
   # )
   created_at = models.DateTimeField(auto_now_add=True)
   completed_at = models.DateTimeField(blank=True, null=True)


   def __str__(self):
       return f"Contribution {self.contribution_id} "
   
   



