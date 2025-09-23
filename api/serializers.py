from rest_framework import serializers
from loans.models import LoanAccount, LoanRepayment, Guarantor
from transaction.models import Transaction
from savings.models import SavingsAccount, SavingsContribution
from vsla.models import VSLA_Account
from pension.models import Pension, PensionAccount
from policy.models import Policy
from django.contrib.auth import authenticate
from users.models import User
import random
from django.core.cache import cache
from rest_framework.validators import UniqueValidator
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from savings.models import SavingsContribution

class LoanAccountSerializer(serializers.ModelSerializer):
    total_interest = serializers.SerializerMethodField()
    total_repayment = serializers.SerializerMethodField()

    class Meta:
        model = LoanAccount
        fields = '__all__'

    def get_total_interest(self, obj):
        
        years = obj.timeline_months / 12
        return (obj.requested_amount * 5.00 * years) / 100

    def get_total_repayment(self, obj):
        
        return obj.requested_amount + self.get_total_interest(obj)

    def validate(self, data):
        member = data.get('member')
        requested_amount = data.get('requested_amount')

        if not member or requested_amount is None:
            return data

        try:
            savings = SavingsAccount.objects.get(member=member)
            max_allowed = savings.member_account_balance * 3
            if requested_amount > max_allowed:
                raise serializers.ValidationError(
                    f"You can only borrow up to 3x your savings (KES {max_allowed:.2f}). "
                    f"Your current savings: KES {savings.member_account_balance:.2f}"
                )
        except SavingsAccount.DoesNotExist:
            raise serializers.ValidationError("You must have a savings account to apply for a loan.")

        return data

    def create(self, validated_data):
        validated_data['loan_status'] = 'DRAFT'
        return super().create(validated_data)


class GuarantorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guarantor
        fields = '__all__'


class LoanRepaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = LoanRepayment
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name', 'phone_number', 'password', 'user_type', 'national_id', 'kra_pin', 'next_of_kin_name', 'email', 'next_of_kin_id']

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    phone_number = serializers.CharField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    user_type = serializers.ChoiceField(choices=[('member', 'Member'), ('manager', 'Manager')])

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'user_type', 'phone_number', 'password', 'national_id', 'kra_pin', 'next_of_kin_name', 'email', 'next_of_kin_id']

    def validate(self, data):
        user_type = data.get('user_type')
        
        if user_type == 'member':
            if not data.get('national_id'):
                raise serializers.ValidationError({"national_id": "This field is required for members."})
            if not data.get('next_of_kin_name'):
                raise serializers.ValidationError({"next_of_kin_name": "This field is required for members."})
        
        elif user_type == 'manager':
            if not data.get('email'):
                raise serializers.ValidationError({"email": "This field is required for managers."})
        else:
            raise serializers.ValidationError({"user_type": "Invalid user type."})
        
        return data


    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        
        if user.email:
            otp_code = str(random.randint(1000, 9999))
            cache.set(
                f"email_otp_{user.id}",
                {
                    'code': otp_code,
                    'expires_at': timezone.now() + timedelta(minutes=10)
                },
                timeout=600
            )
            send_mail(
                'Verify Your Email Address',
                f'Your OTP for email verification is {otp_code}. It is valid for 10 minutes.',
                settings.EMAIL_HOST_USER,
                [user.email],
                fail_silently=False
            )
        return user


class UserLoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        phone_number = data.get("phone_number")
        password = data.get("password")

        if not phone_number or not password:
            raise serializers.ValidationError("Must include 'phone_number' and 'password'.")
        user = authenticate(phone_number=phone_number, password=password)
        if not user:
            raise serializers.ValidationError("Invalid phone number or password")

        if user.user_type not in ["member","manager"]:
            raise serializers.ValidationError("User type not allowed to login")
        data['user'] = user
        return data


class UserProfileSerializer(serializers.ModelSerializer):
    profile_image = serializers.ImageField(required =False,allow_null=True)
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'user_type', 'phone_number','profile_image', 'created_at']


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            user = User.objects.get(email=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User with this email does not exist.")
        otp_code = str(random.randint(1000, 9999))
        cache.set(
            f"otp_{user.id}",
            {
                'code': otp_code,
                'expires_at': timezone.now() + timedelta(minutes=10)
            },
            timeout=600
        )
        send_mail(
            'Your OTP for Password Reset',
            f'Your OTP is {otp_code}. It is valid for 10 minutes.',
            settings.EMAIL_HOST_USER,
            [user.email]
        )
        return value


class ResetPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()
    new_password = serializers.CharField(min_length=8)
    confirm_password = serializers.CharField(write_only=True, min_length=8)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("Password do not match")
        return data

    def save(self, **kwargs):
        user = User.objects.get(email=self.validated_data['email'])
        user.set_password(self.validated_data['new_password'])
        user.save()
        cache.delete(f'otp_{user.id}')
        return user


class VerifyOTPSerializer(serializers.Serializer):
    email = serializers.EmailField()
    otp_code = serializers.CharField(max_length=4)

    def validate(self, data):
        email = data.get('email')
        otp_code = data.get('otp_code')
        try:
            user = User.objects.get(email=email)
            cached_otp = cache.get(f"otp_{user.id}")
            if not cached_otp or cached_otp['code'] != otp_code:
                raise serializers.ValidationError("Invalid OTP.")
            if timezone.now() > cached_otp['expires_at']:
                raise serializers.ValidationError("Expired OTP.")
        except User.DoesNotExist:
            raise serializers.ValidationError("Invalid email.")
        return data


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at']


class SavingsAccountSerializer(serializers.ModelSerializer):
    progress_percentage = serializers.SerializerMethodField()
    savings_target = serializers.SerializerMethodField()
    progress_tier = serializers.SerializerMethodField()

    class Meta:
        model = SavingsAccount
        fields = '__all__'  

    def get_progress_percentage(self, obj):
        target = 1000.00
        if target == 0:
            return 0.0
        percentage = (float(obj.member_account_balance) / target) * 100
        return round(percentage, 2)
    def get_savings_target(self, obj):
        return 1000.00 

    def get_progress_tier(self, obj):
        percentage = self.get_progress_percentage(obj)
        if percentage >= 500:
            return "Super Saver"
        elif percentage >= 300:
            return  "Power Saver"
        elif percentage >= 200:
            return "Strong Saver"
        elif percentage >= 100:
            return "Target Achieved"
        elif percentage >= 50:
            return " On Track"
        else:
            return "Just Starting"








class SavingsContributionSerializer(serializers.ModelSerializer):

    class Meta:
        model = SavingsContribution
        fields = [
            'id',
            'member',
            'saving',
            'contributed_amount',
            'pension_amount',
            'vsla_amount',
            'transaction_id_c2b',
            'transaction_id_b2b',
            'created_at',
            'completed_at',
        ]

    def validate_contributed_amount(self, value):
        if isinstance(value, str):
            value = value.strip()
            if value == '':
                raise serializers.ValidationError("Amount cannot be empty.")
        try:
            return Decimal(str(value))
        except (InvalidOperation, ValueError, TypeError):
            raise serializers.ValidationError("Amount must be a valid number.")

    def validate_pension_amount(self, value):
        if isinstance(value, str):
            value = value.strip()
            if value == '':
                return Decimal('0.00')
        try:
            return Decimal(str(value))
        except (InvalidOperation, ValueError, TypeError):
            raise serializers.ValidationError("Pension amount must be a valid number.")

    def validate_vsla_amount(self, value):
        if isinstance(value, str):
            value = value.strip()
            if value == '':
                return Decimal('0.00')
        try:
            return Decimal(str(value))
        except (InvalidOperation, ValueError, TypeError):
            raise serializers.ValidationError("VSLA amount must be a valid number.")

    def to_representation(self, instance):
        data = super().to_representation(instance)
        member = instance.member
        data['member_first_name'] = member.first_name
        data['member_last_name'] = member.last_name
        data['member_phone'] = member.phone_number
        data['member_national_id'] = member.national_id
        return data

class VSLAAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = VSLA_Account
        fields = [
            "vsla_id",
            "account_name",
            "account_balance",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["vsla_id", "created_at", "updated_at"]


from pension.models import PensionAccount, Pension

class PensionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pension
        fields = ['id', 'name', 'payBill_number', 'status']

class PensionAccountSerializer(serializers.ModelSerializer):
    provider_name = serializers.CharField(source='provider.name', read_only=True)
    provider = serializers.PrimaryKeyRelatedField(
        queryset=Pension.objects.filter(status='active'),
        required=False,
        allow_null=True
    )

    class Meta:
        model = PensionAccount
        fields = [
            'id',
            'is_opted_in',
            'contribution_percentage',
            'total_pension_amount',
            'provider',
            'provider_name',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['total_pension_amount']

    def create(self, validated_data):
        member = self.context['request'].user
        pension_account, created = PensionAccount.objects.get_or_create(
            member=member,
            defaults={
                'is_opted_in': False,
                'contribution_percentage': 0.00
            }
        )        
        for attr, value in validated_data.items():
            setattr(pension_account, attr, value)
        pension_account.save()
        return pension_account

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance


class PolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = Policy
        fields = '__all__'

