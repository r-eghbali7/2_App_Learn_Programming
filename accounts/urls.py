from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    SendOTPView, 
    VerifyOTPView, 
    ResetPasswordView, 
    ChangePasswordView,
    RegisterView,  # اضافه شد
    LoginView      # اضافه شد
)

urlpatterns = [
    # اندپوینت‌های ثبت‌نام و ورود با رمز عبور
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    
    # اندپوینت‌های اصلی OTP
    path('send-otp/', SendOTPView.as_view(), name='send-otp'),
    path('verify-otp/', VerifyOTPView.as_view(), name='verify-otp'),
    path('reset-password/', ResetPasswordView.as_view(), name='reset-password'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]