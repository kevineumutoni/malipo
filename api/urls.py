
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'members', views.MemberViewSet, basename='member')
router.register(r'savings-accounts', views.SavingsAccountViewSet, basename='savingsaccount')
router.register(r'savings-contributions', views.SavingsContributionViewSet, basename='savingscontribution')
router.register(r'vsla-accounts', views.VSLAAccountViewSet, basename='vslaaccount')

urlpatterns = [
    path('', include(router.urls)),
]