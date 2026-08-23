from django.contrib import admin
from .models import User, OTP

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['phone_number', 'full_name', 'is_active', 'is_staff', 'created_at']
    search_fields = ['phone_number', 'full_name']
    list_filter = ['is_active', 'is_staff']

@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ['phone_number', 'code', 'created_at']
    search_fields = ['phone_number']