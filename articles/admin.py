# articles/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import Article
from core.utils import convert_to_shamsi


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ['image_preview', 'title', 'summary_preview', 'is_active', 'created_at_display']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'summary', 'content']
    list_editable = ['is_active']
    readonly_fields = ['created_at', 'large_image_preview']
    actions = ['make_active', 'make_inactive']

    fieldsets = (
        ('اطلاعات مقاله', {
            'fields': ('title', 'summary', 'content')
        }),
        ('تصویر مقاله', {
            'fields': ('image', 'large_image_preview')
        }),
        ('وضعیت و تاریخ', {
            'fields': ('is_active', 'created_at')
        }),
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 50px; object-fit: cover; border-radius: 8px; border: 1px solid #e2e8f0;" />',
                obj.image.url
            )
        return format_html('<span style="color: #94a3b8; font-size: 11px;">بدون تصویر</span>')
    image_preview.short_description = "تصویر"

    def large_image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-width: 320px; max-height: 200px; border-radius: 12px; border: 1px solid #cbd5e1;" />',
                obj.image.url
            )
        return "تصویری آپلود نشده است."
    large_image_preview.short_description = "پیش‌نمایش تصویر"

    def summary_preview(self, obj):
        if len(obj.summary) > 70:
            return obj.summary[:70] + "..."
        return obj.summary
    summary_preview.short_description = "خلاصه"

    def created_at_display(self, obj):
        return convert_to_shamsi(obj.created_at, include_time=True)
    created_at_display.short_description = "تاریخ ایجاد"

    @admin.action(description="فعال‌سازی مقالات انتخاب‌شده")
    def make_active(self, request, queryset):
        queryset.update(is_active=True)

    @admin.action(description="غیرفعال‌سازی مقالات انتخاب‌شده")
    def make_inactive(self, request, queryset):
        queryset.update(is_active=False)