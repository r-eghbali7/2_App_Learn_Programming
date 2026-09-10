# courses/admin.py
from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Course, Chapter, Lesson, CourseEnrollment,
    UserProgress, UserNote, Certificate,
    Quiz, Question, Option, QuizResult,
    LessonQuestion, LessonAnswer
)


class ChapterInline(admin.StackedInline):
    model = Chapter
    extra = 1
    show_change_link = True


class LessonInline(admin.TabularInline):
    model = Lesson
    extra = 1
    fields = ['order', 'title', 'duration_minutes', 'is_free_preview', 'video_url']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['title', 'instructor_display', 'formatted_price', 'access_type_badge', 'enrollments_count', 'is_active', 'created_at']
    list_filter = ['is_active', 'is_free', 'requires_vip', 'created_at']
    search_fields = ['title', 'description', 'instructor__phone_number', 'instructor__full_name', 'instructor_name']
    list_editable = ['is_active']
    inlines = [ChapterInline]
    readonly_fields = ['created_at', 'updated_at']

    def instructor_display(self, obj):
        if obj.instructor:
            return obj.instructor.full_name or obj.instructor.phone_number
        return obj.instructor_name or "تعیین نشده"
    instructor_display.short_description = "مدرس"

    def formatted_price(self, obj):
        if obj.is_free:
            return format_html('<span style="color: green; font-weight: bold;">رایگان</span>')
        return f"{obj.price:,} تومان"
    formatted_price.short_description = "قیمت"

    def access_type_badge(self, obj):
        tags = []
        if obj.requires_vip:
            tags.append('<span style="background: #e0f2fe; color: #0369a1; padding: 2px 6px; border-radius: 4px; font-size: 11px;">VIP</span>')
        if not obj.is_free and obj.price > 0:
            tags.append('<span style="background: #fef3c7; color: #b45309; padding: 2px 6px; border-radius: 4px; font-size: 11px;">خرید تکی</span>')
        return format_html(" ".join(tags)) if tags else "-"
    access_type_badge.short_description = "نوع دسترسی"

    def enrollments_count(self, obj):
        return obj.enrollments.count()
    enrollments_count.short_description = "تعداد خریداران"


@admin.register(Chapter)
class ChapterAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'order', 'lessons_count']
    list_filter = ['course']
    search_fields = ['title', 'course__title']
    ordering = ['course', 'order']
    inlines = [LessonInline]

    def lessons_count(self, obj):
        return obj.lessons.count()
    lessons_count.short_description = "تعداد جلسات"


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ['title', 'get_course_title', 'chapter', 'order', 'duration_minutes', 'is_free_preview']
    list_filter = ['chapter__course', 'is_free_preview']
    search_fields = ['title', 'content', 'chapter__title', 'chapter__course__title']
    list_editable = ['order', 'is_free_preview']

    def get_course_title(self, obj):
        return obj.chapter.course.title
    get_course_title.short_description = "دوره"


@admin.register(CourseEnrollment)
class CourseEnrollmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'course', 'amount_paid', 'purchased_at']
    list_filter = ['course', 'purchased_at']
    search_fields = ['user__phone_number', 'user__full_name', 'course__title']
    readonly_fields = ['purchased_at']


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ['cert_id', 'user', 'course', 'issued_at', 'has_image']
    list_filter = ['course', 'issued_at']
    search_fields = ['cert_id', 'user__phone_number', 'user__full_name', 'course__title']
    readonly_fields = ['cert_id', 'issued_at']

    def has_image(self, obj):
        return bool(obj.image)
    has_image.boolean = True
    has_image.short_description = "تصویر صادر شده"


# ========================================================
# بخش پنل مدیریت آزمون‌ها (Quiz Admin)
# ========================================================

class OptionInline(admin.TabularInline):
    model = Option
    extra = 4
    fields = ['text', 'is_correct']


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['order', 'text_summary', 'quiz', 'options_count']
    list_filter = ['quiz__course', 'quiz']
    search_fields = ['text', 'quiz__title']
    inlines = [OptionInline]

    def text_summary(self, obj):
        return obj.text[:60] + ("..." if len(obj.text) > 60 else "")
    text_summary.short_description = "صورت سوال"

    def options_count(self, obj):
        return obj.options.count()
    options_count.short_description = "تعداد گزینه‌ها"


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ['title', 'course', 'chapter', 'pass_score', 'time_limit_minutes', 'questions_count', 'is_active']
    list_filter = ['course', 'is_active']
    search_fields = ['title', 'course__title']
    list_editable = ['is_active']

    def questions_count(self, obj):
        return obj.questions.count()
    questions_count.short_description = "تعداد سوالات"


@admin.register(QuizResult)
class QuizResultAdmin(admin.ModelAdmin):
    list_display = ['user', 'quiz', 'score_badge', 'attempt_number', 'completed_at']
    list_filter = ['passed', 'quiz__course', 'completed_at']
    search_fields = ['user__phone_number', 'user__full_name', 'quiz__title']
    readonly_fields = ['completed_at']

    def score_badge(self, obj):
        color = "green" if obj.passed else "red"
        status_text = "قبول" if obj.passed else "مردود"
        return format_html(
            '<span style="color: {0}; font-weight: bold;">{1}% ({2})</span>',
            color, obj.score, status_text
        )
    score_badge.short_description = "نمره و وضعیت"


# ========================================================
# بخش پنل مدیریت پرسش و پاسخ (Q&A Admin)
# ========================================================

class LessonAnswerInline(admin.StackedInline):
    model = LessonAnswer
    extra = 1
    fields = ['user', 'content', 'is_instructor_answer', 'is_accepted']


@admin.register(LessonQuestion)
class LessonQuestionAdmin(admin.ModelAdmin):
    list_display = ['title', 'lesson', 'user', 'answers_count', 'is_resolved', 'created_at']
    list_filter = ['is_resolved', 'lesson__chapter__course', 'created_at']
    search_fields = ['title', 'content', 'user__phone_number', 'user__full_name']
    list_editable = ['is_resolved']
    inlines = [LessonAnswerInline]

    def answers_count(self, obj):
        return obj.answers.count()
    answers_count.short_description = "پاسخ‌ها"


@admin.register(UserProgress)
class UserProgressAdmin(admin.ModelAdmin):
    list_display = ['user', 'lesson', 'is_completed', 'completed_at']
    list_filter = ['is_completed', 'lesson__chapter__course']
    search_fields = ['user__phone_number', 'lesson__title']


@admin.register(UserNote)
class UserNoteAdmin(admin.ModelAdmin):
    list_display = ['user', 'lesson', 'updated_at']
    search_fields = ['user__phone_number', 'lesson__title', 'text']