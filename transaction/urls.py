from django.urls import path
from . import views
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import STKPushView, daraja_callback


urlpatterns = [
   path('daraja/stk-push/', STKPushView.as_view(), name='daraja-stk-push'),
   path('daraja/callback/', daraja_callback, name='daraja-callback'),
]


