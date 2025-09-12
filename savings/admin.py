from django.contrib import admin
from .models import SavingsAccount, SavingsContribution

# Register your models here.
admin.site.register(SavingsAccount)
admin.site.register(SavingsContribution)
