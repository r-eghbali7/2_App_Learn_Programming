from django.contrib import admin
from .models import Course, Lesson, UserProgress, UserNote, Certificate

class LessonInline(admin.StackedInline):
    model = Lesson
    extra = 1 # تعداد فرم‌های خالی پیش‌فرض برای افزودن جلسه

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'instructor', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['title', 'instructor']
    inlines = [LessonInline]

@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'lesson', 'is_completed', 'completed_at']
    list_filter = ['is_completed']
    search_fields = ['user__phone_number', 'lesson__title']

@admin.register(UserNote)
class UserNoteAdmin(admin.ModelAdmin):
    list_display = ['user', 'lesson', 'updated_at']
    search_fields = ['user__phone_number', 'lesson__title']

# === بخش مدیریت گواهینامه‌ها ===
@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ['cert_id', 'user', 'course', 'issued_at']
    list_filter = ['course', 'issued_at']
    search_fields = ['cert_id', 'user__phone_number', 'user__full_name', 'course__title']
    readonly_fields = ['cert_id', 'issued_at'] # شماره گواهینامه و تاریخ صدور نباید دستی عوض شوند