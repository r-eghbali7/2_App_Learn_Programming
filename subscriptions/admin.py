# subscriptions/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from .models import Plan, UserSubscription, Transaction
from core.utils import convert_to_shamsi


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = ['title', 'duration_days_display', 'formatted_price', 'active_subscribers_count', 'is_active']
    list_editable = ['is_active']
    search_fields = ['title', 'description']
    ordering = ['price']

    def formatted_price(self, obj):
        return format_html('<span style="font-weight: bold; color: #0284c7;">{:,} تومان</span>', obj.price)
    formatted_price.short_description = "قیمت"

    def duration_days_display(self, obj):
        return f"{obj.duration_days} روزه"
    duration_days_display.short_description = "مدت اعتبار"

    def active_subscribers_count(self, obj):
        return UserSubscription.objects.filter(plan=obj, is_active=True, end_date__gt=timezone.now()).count()
    active_subscribers_count.short_description = "مشترکین فعال"


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user_display', 'plan', 'validity_badge', 'remaining_days_display', 'start_date_display', 'end_date_display']
    list_filter = ['is_active', 'plan', 'end_date']
    search_fields = ['user__phone_number', 'user__full_name', 'plan__title']
    readonly_fields = ['start_date']

    def user_display(self, obj):
        return f"{obj.user.full_name or 'بدون نام'} ({obj.user.phone_number})"
    user_display.short_description = "کاربر"

    def validity_badge(self, obj):
        if obj.is_valid:
            return format_html('<span style="background: #10b981; color: white; padding: 2px 8px; border-radius: 10px; font-size: 11px;">فعال</span>')
        return format_html('<span style="background: #ef4444; color: white; padding: 2px 8px; border-radius: 10px; font-size: 11px;">منقضی شده</span>')
    validity_badge.short_description = "وضعیت"

    def remaining_days_display(self, obj):
        if obj.is_valid:
            delta = (obj.end_date - timezone.now()).days
            return f"{delta} روز باقیمانده"
        return "0 روز"
    remaining_days_display.short_description = "روزهای باقیمانده"

    def start_date_display(self, obj):
        return convert_to_shamsi(obj.start_date, include_time=False)
    start_date_display.short_description = "تاریخ شروع"

    def end_date_display(self, obj):
        return convert_to_shamsi(obj.end_date, include_time=False)
    end_date_display.short_description = "تاریخ پایان"


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['authority_short', 'user_display', 'plan', 'formatted_amount', 'status_badge', 'ref_id', 'created_at_display']
    list_filter = ['status', 'created_at', 'plan']
    search_fields = ['user__phone_number', 'user__full_name', 'authority', 'ref_id']
    readonly_fields = ['user', 'plan', 'authority', 'ref_id', 'amount', 'created_at']

    def authority_short(self, obj):
        return obj.authority[:16] + "..." if len(obj.authority) > 16 else obj.authority
    authority_short.short_description = "شناسه اتوریتی"

    def user_display(self, obj):
        return f"{obj.user.full_name or ''} ({obj.user.phone_number})"
    user_display.short_description = "خریدار"

    def formatted_amount(self, obj):
        return format_html('<b>{:,} تومان</b>', int(obj.amount))
    formatted_amount.short_description = "مبلغ پرداختی"

    def status_badge(self, obj):
        badge_styles = {
            'success': ('#10b981', 'موفق'),
            'failed': ('#ef4444', 'ناموفق'),
            'pending': ('#f59e0b', 'در انتظار پرداخت')
        }
        color, label = badge_styles.get(obj.status, ('#64748b', obj.status))
        return format_html(
            '<span style="background: {0}; color: white; padding: 3px 10px; border-radius: 12px; font-size: 11px; font-weight: bold;">{1}</span>',
            color, label
        )
    status_badge.short_description = "وضعیت تراکنش"

    def created_at_display(self, obj):
        return convert_to_shamsi(obj.created_at, include_time=True)
    created_at_display.short_description = "زمان تراکنش"

    def has_add_permission(self, request):
        return False