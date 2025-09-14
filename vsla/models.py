from django.db import models

class VSLA_Account(models.Model):
    vsla_id = models.AutoField(primary_key=True)
    account_name = models.CharField(max_length=255)
    account_balance = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"VSLA_Account {self.vsla_id}"
