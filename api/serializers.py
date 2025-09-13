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
    email = serializers.EmailField(required=True)
    email = serializers.EmailField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    phone_number = serializers.CharField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'user_type', 'phone_number', 'password','national_id', 'kra_pin', 'next_of_kin_name', 'email','next_of_kin_id']

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
        user = authenticate(phone_number=phone_number, password=password)
        if not user:
            raise serializers.ValidationError("Invalid phone number or password")
        data['user'] = user
        return data

class UserProfileSerializer(serializers.ModelSerializer):
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