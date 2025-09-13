from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views
from .views import PensionViewSet, PolicyViewSet
from django.urls import path, include

from rest_framework.routers import DefaultRouter


router = DefaultRouter()

router.register(
    r"savings-accounts", views.SavingsAccountViewSet, basename="savingsaccount"
)
router.register(
    r"savings-contributions",
    views.SavingsContributionViewSet,
    basename="savingscontribution",
)
router.register(r"vsla-accounts", views.VSLAAccountViewSet, basename="vslaaccount")

urlpatterns = [
    path("", include(router.urls)),
]

router = DefaultRouter()
router.register(r'pensions', PensionViewSet)
router.register(r'policies', PolicyViewSet)

