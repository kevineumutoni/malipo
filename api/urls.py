from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import LoanAccountViewSet, GuarantorViewSet, LoanRepaymentViewSet

router = DefaultRouter()
router.register(r'loan-accounts', LoanAccountViewSet)
router.register(r'guarantors', GuarantorViewSet)
router.register(r'loan-repayments', LoanRepaymentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]