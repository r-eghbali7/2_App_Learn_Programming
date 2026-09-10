# practices/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import Exercise, Submission
from core.utils import convert_to_shamsi


class SubmissionInline(admin.TabularInline):
    model = Submission
    extra = 0
    readonly_fields = ['user', 'status', 'created_at']
    fields = ['user', 'status', 'created_at']
    can_delete = False
    show_change_link = True


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ['title', 'language_badge', 'submissions_count', 'is_active']
    list_filter = ['language', 'is_active']
    search_fields = ['title', 'description', 'starter_code']
    list_editable = ['is_active']
    inlines = [SubmissionInline]

    fieldsets = (
        ('صورت مسئله', {
            'fields': ('title', 'language', 'is_active', 'description')
        }),
        ('کد استارتر', {
            'fields': ('starter_code',),
            'description': 'کدی که در ابتدا درون ادیتور دانشجو قرار می‌گیرد.'
        }),
    )

    def language_badge(self, obj):
        colors = {
            'Python': '#3b82f6',
            'JS': '#eab308',
            'JavaScript': '#eab308',
            'C++': '#6366f1',
            'Java': '#ef4444',
        }
        bg = colors.get(obj.language, '#64748b')
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 8px; border-radius: 4px; font-weight: bold; font-size: 11px;">{}</span>',
            bg, obj.language
        )
    language_badge.short_description = "زبان"

    def submissions_count(self, obj):
        return obj.submissions.count()
    submissions_count.short_description = "تعداد پاسخ‌ها"


@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['user_info', 'exercise', 'status_badge', 'created_at_display']
    list_filter = ['status', 'exercise__language', 'created_at']
    search_fields = ['user__phone_number', 'user__full_name', 'exercise__title', 'submitted_code']
    readonly_fields = ['user', 'exercise', 'submitted_code_box', 'feedback_box', 'created_at']

    fieldsets = (
        ('اطلاعات ارسال', {
            'fields': ('user', 'exercise', 'status', 'created_at')
        }),
        ('کد ارسالی دانشجو', {
            'fields': ('submitted_code_box',)
        }),
        ('خروجی و بازخورد سیستم', {
            'fields': ('feedback_box',)
        }),
    )

    def user_info(self, obj):
        return f"{obj.user.full_name or 'بدون نام'} ({obj.user.phone_number})"
    user_info.short_description = "دانشجو"

    def status_badge(self, obj):
        badge_styles = {
            'passed': ('#10b981', 'تایید شده (Passed)'),
            'failed': ('#ef4444', 'رد شده (Failed)'),
            'pending': ('#f59e0b', 'در حال بررسی (Pending)')
        }
        color, label = badge_styles.get(obj.status, ('#64748b', obj.status))
        return format_html(
            '<span style="background: {0}; color: white; padding: 3px 10px; border-radius: 12px; font-size: 11px; font-weight: bold;">{1}</span>',
            color, label
        )
    status_badge.short_description = "وضعیت ارزیابی"

    def submitted_code_box(self, obj):
        return format_html(
            '<pre style="background: #0f172a; color: #38bdf8; padding: 16px; border-radius: 8px; font-family: monospace; font-size: 13px; max-height: 350px; overflow-y: auto; direction: ltr; text-align: left;">{}</pre>',
            obj.submitted_code
        )
    submitted_code_box.short_description = "کد اجرا شده"

    def feedback_box(self, obj):
        if not obj.feedback:
            return "بازخوردی ثبت نشده است."
        return format_html(
            '<pre style="background: #1e293b; color: #e2e8f0; padding: 14px; border-radius: 8px; font-family: monospace; font-size: 12px; max-height: 200px; overflow-y: auto; direction: ltr; text-align: left;">{}</pre>',
            obj.feedback
        )
    feedback_box.short_description = "خروجی کنسول سرور"

    def created_at_display(self, obj):
        return convert_to_shamsi(obj.created_at, include_time=True)
    created_at_display.short_description = "زمان ارسال"

    def has_add_permission(self, request):
        return False