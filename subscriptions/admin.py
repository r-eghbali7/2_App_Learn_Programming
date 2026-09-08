# subscriptions/admin.py
from django.contrib import admin
from .models import Plan, UserSubscription, Transaction

@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ['title', 'duration_days', 'price', 'is_active']
    list_editable = ['is_active', 'price']
    search_fields = ['title']
    ordering = ['id']

@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'plan', 'start_date', 'end_date', 'is_active', 'is_valid']
    list_filter = ['is_active', 'plan']
    search_fields = ['user__phone_number', 'user__full_name']
    readonly_fields = ['start_date']

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'plan', 'amount', 'status', 'ref_id', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['user__phone_number', 'authority', 'ref_id']
    readonly_fields = ['created_at', 'authority']