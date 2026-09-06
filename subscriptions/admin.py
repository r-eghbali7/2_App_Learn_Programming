from django.contrib import admin
from .models import Plan, UserSubscription, Transaction

@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ['title', 'duration_days', 'price', 'is_active']
    list_editable = ['is_active', 'price'] # امکان تغییر سریع قیمت و وضعیت از همان صفحه لیست
    search_fields = ['title']

@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    # is_valid یک @property در مدل شماست و اینجا به صورت خودکار محاسبه و نمایش داده می‌شود
    list_display = ['user', 'plan', 'start_date', 'end_date', 'is_active', 'is_valid']
    list_filter = ['is_active', 'plan']
    search_fields = ['user__phone_number', 'user__full_name']
    readonly_fields = ['start_date']

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'amount', 'is_paid', 'ref_id', 'created_at']
    list_filter = ['is_paid']
    search_fields = ['user__phone_number', 'authority', 'ref_id']
    readonly_fields = ['created_at']