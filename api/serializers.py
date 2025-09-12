from rest_framework import serializers
from loans.models import LoanAccount,LoanRepayment,Guarantor

class LoanAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanAccount
        fields = '__all__'

class GuarantorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guarantor
        fields = '__all__'

class LoanRepaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanRepayment
        fields = '__all__'