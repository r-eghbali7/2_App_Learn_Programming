# tickets/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import Ticket
from core.utils import convert_to_shamsi


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['id', 'user_display', 'subject_badge', 'message_snippet', 'attachment_link', 'status', 'created_at_display']
    list_filter = ['status', 'subject', 'created_at']
    search_fields = ['user__phone_number', 'user__full_name', 'message']
    list_editable = ['status']
    readonly_fields = ['created_at', 'attachment_preview']

    fieldsets = (
        ('مشخصات تیکت', {
            'fields': ('user', 'subject', 'status', 'created_at')
        }),
        ('متن پیام', {
            'fields': ('message',)
        }),
        ('فایل ضمیمه', {
            'fields': ('attachment', 'attachment_preview')
        }),
    )

    def user_display(self, obj):
        return f"{obj.user.full_name or 'بدون نام'} ({obj.user.phone_number})"
    user_display.short_description = "کاربر ارسال‌کننده"

    def subject_badge(self, obj):
        colors = {
            'technical': ('#ef4444', 'پشتیبانی فنی'),
            'financial': ('#10b981', 'امور مالی'),
            'educational': ('#3b82f6', 'آموزشی'),
            'other': ('#64748b', 'سایر')
        }
        color, label = colors.get(obj.subject, ('#64748b', obj.get_subject_display()))
        return format_html(
            '<span style="background: {0}; color: white; padding: 2px 8px; border-radius: 4px; font-size: 11px;">{1}</span>',
            color, label
        )
    subject_badge.short_description = "موضوع"

    def message_snippet(self, obj):
        return obj.message[:60] + ("..." if len(obj.message) > 60 else "")
    message_snippet.short_description = "متن پیام"

    def attachment_link(self, obj):
        if obj.attachment:
            return format_html(
                '<a href="{}" target="_blank" style="color: #0284c7; font-weight: bold;">دانلود فایل 📎</a>',
                obj.attachment.url
            )
        return format_html('<span style="color: #94a3b8;">ندارد</span>')
    attachment_link.short_description = "ضمیمه"

    def attachment_preview(self, obj):
        if obj.attachment:
            url = obj.attachment.url
            if any(url.lower().endswith(ext) for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                return format_html('<img src="{}" style="max-width: 300px; border-radius: 8px;" />', url)
            return format_html('<a href="{}" target="_blank">مشاهده / دریافت فایل ضمیمه</a>', url)
        return "فایلی ضمیمه نشده است."
    attachment_preview.short_description = "پیش‌نمایش ضمیمه"

    def created_at_display(self, obj):
        return convert_to_shamsi(obj.created_at, include_time=True)
    created_at_display.short_description = "زمان ارسال"