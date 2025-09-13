from . import views
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import STKPushView, daraja_callback, b2c_callback, b2b_callback 


urlpatterns = [
   path('daraja/stk-push/', STKPushView.as_view(), name='daraja-stk-push'),
   path('daraja/callback/', daraja_callback, name='daraja-callback'), 
   path('daraja/b2c-payment/', views.B2CPaymentView.as_view(), name='b2c_payment'),
   path('daraja/b2c-callback/', views.b2c_callback, name='b2c_callback'),
   path('daraja/b2b-callback/', b2b_callback, name='b2b_callback'),
]


