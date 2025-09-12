
from rest_framework import serializers
from users.models import Member
from savings.models import SavingsAccount, SavingsContribution
from vsla.models import VSLA_Account

class MemberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Member
        fields = ['member_id']

class SavingsAccountSerializer(serializers.ModelSerializer):
    member = MemberSerializer(read_only=True)
    class Meta:
        model = SavingsAccount
        fields = [
            'saving_id', 'member', 'member_id',
            'member_account_balance', 'interest_incurred',
            'created_at', 'updated_at'
        ]


class SavingsContributionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavingsContribution
        fields = [
            'contribution_id', 'saving', 'saving_id',
            'contributed_amount', 'pension_percentage',
            'pension_amount', 'vsla_amount',
            'created_at', 'completed_at'
        ]
    def validate(self, data):
        contributed_amount = data.get('contributed_amount')
        pension_percentage = data.get('pension_percentage', 0)

        if pension_percentage < 0 or pension_percentage > 100:
            raise serializers.ValidationError({
                'pension_percentage': 'Must be between 0 and 100.'
            })

    
        pension_amount = round(contributed_amount * (pension_percentage / 100), 2)
        vsla_amount = round(contributed_amount - pension_amount, 2)
        return data

    def create(self, validated_data):
        saving_id = validated_data.pop('saving_id')
        try:
            saving = SavingsAccount.objects.get(saving_id=saving_id)
        except SavingsAccount.DoesNotExist:
            raise serializers.ValidationError({"saving_id": "Savings account does not exist."})

        return SavingsContribution.objects.create(saving=saving, **validated_data)
    
    

class VSLAAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = VSLA_Account
        fields = [
            'vsla_id', 'account_name', 'account_balance',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['vsla_id', 'created_at', 'updated_at']