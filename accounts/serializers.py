# accounts/serializers.py
from rest_framework import serializers
import re

def validate_iranian_phone(value):
    if not re.match(r'^09\d{9}$', value):
        raise serializers.ValidationError("شماره موبایل معتبر نیست. مثال: 09123456789")
    return value

class SendOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=11, validators=[validate_iranian_phone])

class VerifyOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=11, validators=[validate_iranian_phone])
    code = serializers.CharField(max_length=6)
    # فیلدهای اختیاری برای زمانی که کاربر بار اول ثبت‌نام می‌کند
    full_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    password = serializers.CharField(max_length=128, required=False, allow_blank=True)
    
class ResetPasswordSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=11, validators=[validate_iranian_phone])
    code = serializers.CharField(max_length=6)
    new_password = serializers.CharField(max_length=128, min_length=6)

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(max_length=128)
    new_password = serializers.CharField(max_length=128, min_length=6)