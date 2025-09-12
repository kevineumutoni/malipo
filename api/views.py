from django.shortcuts import render
from rest_framework import viewsets
from loans.models import LoanAccount, Guarantor, LoanRepayment
from .serializers import LoanAccountSerializer, GuarantorSerializer, LoanRepaymentSerializer

class LoanAccountViewSet(viewsets.ModelViewSet):
    queryset = LoanAccount.objects.all()
    serializer_class = LoanAccountSerializer

class GuarantorViewSet(viewsets.ModelViewSet):
    queryset = Guarantor.objects.all()
    serializer_class = GuarantorSerializer

class LoanRepaymentViewSet(viewsets.ModelViewSet):
    queryset = LoanRepayment.objects.all()
    serializer_class = LoanRepaymentSerializer