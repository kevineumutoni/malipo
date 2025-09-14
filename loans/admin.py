from django.contrib import admin
from .models import LoanAccount, Guarantor, LoanRepayment

admin.site.register(LoanAccount)
admin.site.register(Guarantor)
admin.site.register(LoanRepayment)
