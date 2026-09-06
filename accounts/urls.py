# accounts/urls.py
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView  # این خط اضافه شد

from .views import (
    SendOTPView, 
    VerifyOTPView, 
    ResetPasswordView, 
    ChangePasswordView
)

urlpatterns = [
    # اندپوینت‌های اصلی
    path('send-otp/', SendOTPView.as_view(), name='send-otp'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    
    # اندپوینت تمدید توکن
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]