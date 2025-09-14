from rest_framework import serializers
from transaction.models import Transaction  
from savings.models import SavingsAccount, SavingsContribution
from vsla.models import VSLA_Account
from pension.models import Pension
from policy.models import  Policy 
from rest_framework import serializers
from django.contrib.auth import authenticate
from users.models import User
import random
from django.core.cache import cache
from rest_framework.validators import UniqueValidator
from django.core.mail import send_mail
from django.utils import timezone
from datetime import timedelta
from django.conf import settings

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['id', 'first_name', 'last_name','phone_number', 'password','user_type', 'national_id', 'kra_pin', 'next_of_kin_name', 'email','next_of_kin_id']

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
        fields = ['first_name', 'last_name', 'user_type', 'phone_number', 'created_at']


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
    confirm_password = serializers.CharField(write_only = True, min_length=8)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("Password do not match")
        return data
    def save(self, **kwargs):
        user=User.objects.get(email=self.validated_data['email'])
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
 class Meta:
        model = SavingsAccount
        fields = [
            "saving_id",
            "member",
            "member_id",
            "member_account_balance",
            "interest_incurred",
            "created_at",
            "updated_at",
        ]

class SavingsContributionSerializer(serializers.ModelSerializer):
    class Meta:
        model = SavingsContribution
        fields = [
            "contribution_id",
            "saving",
            "saving_id",
            "contributed_amount",
            "pension_percentage",
            "pension_amount",
            "vsla_amount",
            "created_at",
            "completed_at",
        ]

    def validate(self, data):
        contributed_amount = data.get("contributed_amount")
        pension_percentage = data.get("pension_percentage", 0)

        if pension_percentage < 0 or pension_percentage > 100:
            raise serializers.ValidationError(
                {"pension_percentage": "Must be between 0 and 100."}
            )

        pension_amount = round(contributed_amount * (pension_percentage / 100), 2)
        vsla_amount = round(contributed_amount - pension_amount, 2)
        return data

    def create(self, validated_data):
        saving_id = validated_data.pop("saving_id")
        try:
            saving = SavingsAccount.objects.get(saving_id=saving_id)
        except SavingsAccount.DoesNotExist:
            raise serializers.ValidationError(
                {"saving_id": "Savings account does not exist."}
            )

        return SavingsContribution.objects.create(saving=saving, **validated_data)


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

class PensionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pension
        fields = '__all__'  


class PolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = Policy
        fields = '__all__'  
