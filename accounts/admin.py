# accounts/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from django.utils import timezone
from .models import User, OTP


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """
    پنل مدیریت اختصاصی و ایمن برای کاربر سفارشی مبتنی بر شماره موبایل
    """
    # ستون‌های نمایش داده شده در لیست
    list_display = [
        'phone_number',
        'full_name_display',
        'role_badge',
        'subscription_status_badge',
        'is_active',
        'created_at_display'
    ]
    
    # فیلترهای کناری
    list_filter = ['is_active', 'is_staff', 'is_superuser', 'created_at']
    
    # فیلدهای قابل جستجو
    search_fields = ['phone_number', 'full_name']
    
    # مرتب‌سازی پیش‌فرض (جدیدترین کاربران در بالا)
    ordering = ['-created_at']
    
    # ویرایش سریع وضعیت فعال/غیرفعال از همان صفحه لیست
    list_editable = ['is_active']
    
    readonly_fields = ['created_at', 'last_login']

    # سازمان‌دهی فیلدها در فرم ویرایش کاربر
    fieldsets = (
        ('اطلاعات هویتی و حساب', {
            'fields': ('phone_number', 'password')
        }),
        ('اطلاعات فردی', {
            'fields': ('full_name',)
        }),
        ('سطوح دسترسی و وضعیت', {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions'
            ),
            'classes': ('collapse',),  # امکان جمع‌شدن این بخش برای شلوغ نشدن صفحه
        }),
        ('تاریخچه‌ها', {
            'fields': ('created_at', 'last_login'),
            'classes': ('collapse',),
        }),
    )

    # فیلدهای فرم هنگام ساخت دستی کاربر از درون پنل ادمین
    add_fieldsets = (
        ('افزودن کاربر جدید', {
            'classes': ('wide',),
            'fields': ('phone_number', 'full_name', 'password', 'is_staff', 'is_active'),
        }),
    )

    # --- متدهای کمکی و نمایشی (Custom Display Methods) ---

    def full_name_display(self, obj):
        return obj.full_name if obj.full_name else format_html('<span style="color: #94a3b8;">(بدون نام)</span>')
    full_name_display.short_description = "نام و نام خانوادگی"

    def role_badge(self, obj):
        if obj.is_superuser:
            return format_html('<span style="background: #ef4444; color: white; padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: bold;">مدیر کل</span>')
        elif obj.is_staff:
            return format_html('<span style="background: #3b82f6; color: white; padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: bold;">ادمین / مدرس</span>')
        return format_html('<span style="background: #64748b; color: white; padding: 3px 8px; border-radius: 4px; font-size: 11px;">دانشجو</span>')
    role_badge.short_description = "نقش"

    def subscription_status_badge(self, obj):
        """نمایش وضعیت اشتراک ویژه کاربر"""
        # ایمپورت داخلی برای جلوگیری از Circular Import
        from subscriptions.models import UserSubscription
        
        active_sub = UserSubscription.objects.filter(
            user=obj,
            is_active=True,
            end_date__gt=timezone.now()
        ).order_by('-end_date').first()
        
        if active_sub:
            days_left = (active_sub.end_date - timezone.now()).days
            return format_html(
                '<span style="background: #10b981; color: white; padding: 3px 8px; border-radius: 4px; font-size: 11px; font-weight: bold;">VIP ({} روز)</span>',
                days_left
            )
        return format_html('<span style="color: #94a3b8; font-size: 11px;">عادی</span>')
    subscription_status_badge.short_description = "اشتراک"

    def created_at_display(self, obj):
        from core.utils import convert_to_shamsi
        return convert_to_shamsi(obj.created_at, include_time=True)
    created_at_display.short_description = "تاریخ عضویت"


@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    """
    پنل مدیریت کدهای یکبار مصرف به همراه وضعیت اعتبار و ابزار پاکسازی
    """
    list_display = ['phone_number', 'code', 'status_badge', 'created_at_display']
    search_fields = ['phone_number', 'code']
    list_filter = ['created_at']
    readonly_fields = ['phone_number', 'code', 'created_at']
    ordering = ['-created_at']

    # اضافه کردن دکمه اقدام اختصاصی (Action) برای حذف کدهای منقضی‌شده
    actions = ['delete_expired_otps']

    def status_badge(self, obj):
        if obj.is_valid():
            return format_html(
                '<span style="background: #22c55e; color: white; padding: 2px 8px; border-radius: 12px; font-size: 11px;">معتبر</span>'
            )
        return format_html(
            '<span style="background: #ef4444; color: white; padding: 2px 8px; border-radius: 12px; font-size: 11px;">منقضی شده</span>'
        )
    status_badge.short_description = "وضعیت کد"

    def created_at_display(self, obj):
        from core.utils import convert_to_shamsi
        return convert_to_shamsi(obj.created_at, include_time=True)
    created_at_display.short_description = "زمان ارسال"

    @admin.action(description="حذف تمامی کدهای تایید منقضی‌شده")
    def delete_expired_otps(self, request, queryset):
        import datetime
        expiration_limit = timezone.now() - datetime.timedelta(minutes=2)
        count, _ = OTP.objects.filter(created_at__lt=expiration_limit).delete()
        self.message_user(request, f"{count} کد منقضی‌شده با موفقیت از دیتابیس حذف شدند.")

    def has_add_permission(self, request):
        # جلوگیری از ساخت دستی OTP از پنل ادمین (چون باید توسط سیستم و پیامک ساخته شود)
        return False