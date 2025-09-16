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
from rest_framework.permissions import AllowAny
from rest_framework.authentication import BasicAuthentication
from rest_framework import permissions
from rest_framework import viewsets, status, generics
from rest_framework.response import Response
from .serializers import PensionSerializer, PolicySerializer
from pension.models import Pension, PensionAccount
from policy.models import Policy
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token
from django_filters.rest_framework import DjangoFilterBackend
from users.models import User
from .serializers import UserRegisterSerializer, UserLoginSerializer, UserProfileSerializer,ForgotPasswordSerializer,ResetPasswordSerializer,VerifyOTPSerializer
from .serializers import UserSerializer
from rest_framework.decorators import action, api_view
from django.utils import timezone
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from savings.models import SavingsContribution


class LoanAccountViewSet(viewsets.ModelViewSet):
    queryset = LoanAccount.objects.all()
    serializer_class = LoanAccountSerializer

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        loan = self.get_object()
        action = request.data.get('action', '').lower()
        reason = request.data.get('reason', '')

        if loan.loan_status != 'PENDING_MANAGER':
            return Response({"error": "Loan is not pending manager approval."}, status=400)

        if action == 'approve':
            loan.loan_status = 'APPROVED'
            notification = "Your loan has been approved. Funds will be sent shortly."
        elif action == 'reject':
            loan.loan_status = 'REJECTED'
            loan.rejection_reason = reason
            notification = f"Your loan was rejected. Reason: {reason}"
        else:
            return Response({"error": "Action must be 'approve' or 'reject'"}, status=400)

        loan.approved_at = timezone.now()
        loan.save()

        return Response({
            "message": f"Loan {action}ed successfully.",
            "notification": notification,
            "status": loan.loan_status
        })


class GuarantorViewSet(viewsets.ModelViewSet):
    queryset = Guarantor.objects.all()
    serializer_class = GuarantorSerializer

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        guarantor = self.get_queryset().get(id=response.data['id'])
        
        notification_msg = (
            f"You’ve been requested to guarantee a loan of KES {guarantor.loan.requested_amount:,.2f} "
            f"for {guarantor.loan.member.first_name}. Please respond in the app."
        )
        
        response.data['notification'] = notification_msg
        return response

    @action(detail=True, methods=['post'])
    def respond(self, request, pk=None):
        guarantor = self.get_object()
        action = request.data.get('action', '').lower()

        if action not in ['approve', 'reject']:
            return Response({"error": "Action must be 'approve' or 'reject'"}, status=400)

        if guarantor.status != 'Pending':
            return Response({"error": "Already responded or expired."}, status=400)

        if action == 'approve':
            guarantor.status = 'Approved'
        else:
            guarantor.status = 'Rejected'
        guarantor.responded_at = timezone.now()
        guarantor.save()

        if action == 'approve':
            loan = guarantor.loan
            loan.loan_status = 'PENDING_MANAGER'
            loan.save()

        if action == 'reject':
            msg = f"Your guarantor {guarantor.guarantor_name} rejected your loan. Add a new one."
        else:
            msg = f"{guarantor.guarantor_name} approved your loan. Waiting for manager."

        return Response({
            "message": f"Guarantor request {action}ed.",
            "notification": msg,
            "status": guarantor.status
        })

    @action(detail=True, methods=['get'])
    def check_status(self, request, pk=None):
        """
        GET /api/guarantors/{id}/check_status/
        Returns status + notification if expired.
        """
        guarantor = self.get_object()
        data = {
            "id": guarantor.id,
            "loan_id": guarantor.loan.id,
            "guarantor_name": guarantor.guarantor_name,
            "status": guarantor.status,
            "created_at": guarantor.created_at,
            "responded_at": guarantor.responded_at,
        }

        if guarantor.status == 'Expired':
            data["notification"] = (
                f"Your guarantor request for '{guarantor.guarantor_name}' has expired. "
                f"Please add a new guarantor for your loan (ID: {guarantor.loan.id})."
            )

        return Response(data)


@api_view(['POST'])
def expire_guarantors_manual(request):
    """
    POST /api/expire-guarantors/
    Manually expire all pending guarantor requests older than 24 hours.
    """
    expired_count = Guarantor.objects.filter(
        status='Pending',
        created_at__lt=timezone.now() - timedelta(hours=24)
    ).update(
        status='Expired',
        updated_at=timezone.now()
    )

    return Response({
        "message": f"Successfully expired {expired_count} guarantor request(s).",
        "status": "success"
    })
class LoanRepaymentViewSet(viewsets.ModelViewSet):
    queryset = LoanRepayment.objects.all()
    serializer_class = LoanRepaymentSerializer
    




class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['user_type']


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


    from rest_framework.decorators import action

    @action(detail=False, methods=['post'])
    def apply_interest(self, request):
        """
        POST /api/savings-accounts/apply_interest/
        Apply annual interest to all savings accounts.
        """
        accounts = self.get_queryset()
        results = []

        for account in accounts:
            interest = (account.member_account_balance * 2.50) / 100  
            account.member_account_balance += interest
            account.interest_incurred += interest
            account.save()

            results.append({
                "member": account.member.first_name,
                "interest_applied": float(interest),
                "new_balance": float(account.member_account_balance)
            })

        return Response({
            "message": "Annual interest applied successfully.",
            "results": results
        })




from rest_framework import viewsets
from savings.models import SavingsContribution
from .serializers import SavingsContributionSerializer

class SavingsContributionViewSet(viewsets.ModelViewSet):
    serializer_class = SavingsContributionSerializer
    queryset = SavingsContribution.objects.all()

    def get_queryset(self):
        return self.queryset.filter(member=self.request.user)

    def perform_create(self, serializer):
        serializer.save()


class VSLAAccountViewSet(viewsets.ModelViewSet):
    queryset = VSLA_Account.objects.all()
    serializer_class = VSLAAccountSerializer
    lookup_field = "vsla_id"


class PensionViewSet(viewsets.ModelViewSet):
    queryset = Pension.objects.all()
    serializer_class = PensionSerializer


from rest_framework import generics
from pension.models import Pension
from .serializers import PensionSerializer

class PensionProviderListView(generics.ListAPIView):
    serializer_class = PensionSerializer
    queryset = Pension.objects.filter(status='active')


class PolicyViewSet(viewsets.ModelViewSet):
    queryset = Policy.objects.all()
    serializer_class = PolicySerializer



class PensionAccountViewSet(viewsets.ModelViewSet):
    serializer_class = PensionAccountSerializer
    queryset = PensionAccount.objects.all()

    def get_queryset(self):
        return self.queryset.filter(member=self.request.user)

    def perform_create(self, serializer):
        serializer.save(member=self.request.user)

   
