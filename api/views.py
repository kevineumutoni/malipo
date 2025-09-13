from django.shortcuts import render
from rest_framework import viewsets
from loans.models import LoanAccount, Guarantor, LoanRepayment
from .serializers import LoanAccountSerializer, GuarantorSerializer, LoanRepaymentSerializer
from rest_framework.permissions import IsAuthenticated
from transaction.models import Transaction 
from .serializers import TransactionSerializer 
from users.models import Member
from savings.models import SavingsAccount
from savings.models import SavingsContribution
from vsla.models import VSLA_Account
from .serializers import (
    SavingsAccountSerializer,
    SavingsContributionSerializer,
    VSLAAccountSerializer,
    PensionAccountSerializer,
)
from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from .serializers import PensionSerializer, PolicySerializer
from pension.models import Pension, PensionAccount
from policy.models import Policy
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from users.models import User
from .serializers import UserRegisterSerializer, UserLoginSerializer, UserProfileSerializer,ForgotPasswordSerializer,ResetPasswordSerializer,VerifyOTPSerializer
from .serializers import UserSerializer
 

class LoanAccountViewSet(viewsets.ModelViewSet):
    queryset = LoanAccount.objects.all()
    serializer_class = LoanAccountSerializer

class GuarantorViewSet(viewsets.ModelViewSet):
    queryset = Guarantor.objects.all()
    serializer_class = GuarantorSerializer

class LoanRepaymentViewSet(viewsets.ModelViewSet):
    queryset = LoanRepayment.objects.all()
    serializer_class = LoanRepaymentSerializer



class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegisterSerializer

class LoginView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]

        token, _ = Token.objects.get_or_create(user=user)
        return Response({
            "token": str(token.key),
            "user": {
                "user_id": str(user.id),  
                "first_name": user.first_name,
                "last_name": user.last_name,
                "user_type": user.user_type,
                "phone_number": user.phone_number,
            }
        })

class ProfileView(generics.RetrieveAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    def get_object(self):
        return self.request.user

class ForgotPasswordView(generics.GenericAPIView):
    serializer_class = ForgotPasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({"message": "OTP sent to your email"}, status=status.HTTP_200_OK)


class ResetPasswordView(generics.GenericAPIView):
    serializer_class = ResetPasswordSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"message": "Password reset successfully"}, status=status.HTTP_200_OK)


class VerifyOTPView(generics.GenericAPIView):
    serializer_class = VerifyOTPSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        return Response({"message": "OTP verified successfully"}, status=status.HTTP_200_OK)
        return Response({"message": "OTP verified successfully"}, status=status.HTTP_200_OK)



class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
   
class SavingsAccountViewSet(viewsets.ModelViewSet):
    queryset = SavingsAccount.objects.select_related("member").all()
    serializer_class = SavingsAccountSerializer
    lookup_field = "saving_id"


class SavingsContributionViewSet(viewsets.ModelViewSet):
    queryset = SavingsContribution.objects.select_related("saving__member").all()
    serializer_class = SavingsContributionSerializer
    lookup_field = "contribution_id"


class VSLAAccountViewSet(viewsets.ModelViewSet):
    queryset = VSLA_Account.objects.all()
    serializer_class = VSLAAccountSerializer
    lookup_field = "vsla_id"


class PensionViewSet(viewsets.ModelViewSet):
    queryset = Pension.objects.all()
    serializer_class = PensionSerializer



class PensionAccountViewSet(viewsets.ModelViewSet):
    queryset = PensionAccount.objects.all()
    serializer_class = PensionAccountSerializer


class PolicyViewSet(viewsets.ModelViewSet):
    queryset = Policy.objects.all()
    serializer_class = PolicySerializer

   
