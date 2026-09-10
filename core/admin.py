# core/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import Banner
from core.utils import convert_to_shamsi


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ['banner_thumbnail', 'title', 'link_preview', 'is_active', 'created_at_display']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'link']
    list_editable = ['is_active']
    readonly_fields = ['created_at', 'banner_large_preview']

    fieldsets = (
        ('مشخصات بنر', {
            'fields': ('title', 'link')
        }),
        ('تصویر بنر', {
            'fields': ('image', 'banner_large_preview')
        }),
        ('تنظیمات انتشار', {
            'fields': ('is_active', 'created_at')
        }),
    )

    def banner_thumbnail(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 100px; height: 45px; object-fit: cover; border-radius: 6px;" />',
                obj.image.url
            )
        return "-"
    banner_thumbnail.short_description = "تصویر"

    def banner_large_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="max-width: 450px; border-radius: 8px;" />', obj.image.url)
        return "تصویری وجود ندارد."
    banner_large_preview.short_description = "پیش‌نمایش تصویر"

    def link_preview(self, obj):
        if obj.link:
            return format_html(
                '<a href="{}" target="_blank" style="color: #0284c7; text-decoration: none;">باز کردن لینک ↗</a>',
                obj.link
            )
        return format_html('<span style="color: #94a3b8;">ندارد</span>')
    link_preview.short_description = "لینک مقصد"

    def created_at_display(self, obj):
        return convert_to_shamsi(obj.created_at, include_time=False)
    created_at_display.short_description = "تاریخ ثبت"