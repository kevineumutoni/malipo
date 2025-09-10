from .views import PensionViewSet, PolicyViewSet
from django.urls import path, include

from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'pensions', PensionViewSet)
router.register(r'policies', PolicyViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
