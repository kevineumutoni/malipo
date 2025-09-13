from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LoanAccountViewSet, GuarantorViewSet, LoanRepaymentViewSet
from .views import TransactionViewSet 
from . import views
from .views import PensionViewSet, PolicyViewSet
from .views import RegisterView, LoginView, ProfileView, UserViewSet, ForgotPasswordView, VerifyOTPView, ResetPasswordView
from rest_framework.authtoken.views import obtain_auth_token

router = DefaultRouter()
router.register(r'loan-accounts', LoanAccountViewSet)
router.register(r'guarantors', GuarantorViewSet)
router.register(r'loan-repayments', LoanRepaymentViewSet)
router.register(r'users', UserViewSet, basename='user')
router.register(r'pensions', PensionViewSet)
router.register(r'policies', PolicyViewSet)
router.register(r'transactions', TransactionViewSet, basename='transaction')
router.register(r"savings-accounts", views.SavingsAccountViewSet, basename="savingsaccount")
router.register(r"savings-contributions", views.SavingsContributionViewSet, basename="savingscontribution",)
router.register(r"vsla-accounts", views.VSLAAccountViewSet, basename="vslaaccount")

urlpatterns = [
    path("", include(router.urls)),
    path('api/', include(router.urls)),  
    path('api/register/', RegisterView.as_view(), name='register'),
    path('api/login/', LoginView.as_view(), name='login'),
    path('api/profile/', ProfileView.as_view(), name='profile'),
    path('api/forgot-password/', ForgotPasswordView.as_view(), name='forgot-password'),
    path('api/verify-code/', VerifyOTPView.as_view(), name='verify-code'),
    path('api/reset-password/', ResetPasswordView.as_view(), name='reset-password'),    
    path('api/reset-password/', ResetPasswordView.as_view(), name='reset-password'),
]

    

