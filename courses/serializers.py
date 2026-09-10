# courses/serializers.py
from rest_framework import serializers
from .models import Certificate, Course, Chapter, Lesson, UserProgress, UserNote, Quiz, CourseEnrollment


class UserNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserNote
        fields = ['id', 'text', 'updated_at']


class LessonSerializer(serializers.ModelSerializer):
    is_completed = serializers.SerializerMethodField()
    user_note = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = ['id', 'title', 'content', 'video_url', 'duration_minutes', 'order', 'is_free_preview', 'is_completed', 'user_note']

    def get_is_completed(self, obj):
        user = self.context.get('request') and self.context['request'].user
        if user and user.is_authenticated:
            if hasattr(obj, 'user_progress'):
                return len(obj.user_progress) > 0
            return UserProgress.objects.filter(user=user, lesson=obj, is_completed=True).exists()
        return False

    def get_user_note(self, obj):
        user = self.context.get('request') and self.context['request'].user
        if user and user.is_authenticated:
            if hasattr(obj, 'user_notes'):
                return UserNoteSerializer(obj.user_notes[0]).data if obj.user_notes else None
            note = UserNote.objects.filter(user=user, lesson=obj).first()
            return UserNoteSerializer(note).data if note else None
        return None


class ChapterSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)

    class Meta:
        model = Chapter
        fields = ['id', 'title', 'order', 'lessons']


class CourseListSerializer(serializers.ModelSerializer):
    instructor_display = serializers.SerializerMethodField()
    lessons_count = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ['id', 'title', 'thumbnail', 'instructor_display', 'price', 'is_free', 'requires_vip', 'lessons_count']

    def get_instructor_display(self, obj):
        if obj.instructor:
            return obj.instructor.full_name or obj.instructor.phone_number
        return obj.instructor_name or "مدرس آکادمی"

    def get_lessons_count(self, obj):
        return obj.total_lessons_count


class CourseDetailSerializer(serializers.ModelSerializer):
    chapters = ChapterSerializer(many=True, read_only=True)
    lessons = serializers.SerializerMethodField()  # جهت سازگاری ۱۰۰٪ با کلاینت قبلی فلاتر
    progress_percentage = serializers.SerializerMethodField()
    instructor_display = serializers.SerializerMethodField()
    is_enrolled = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = [
            'id', 'title', 'description', 'thumbnail', 'price', 'is_free', 
            'requires_vip', 'instructor_display', 'progress_percentage', 
            'is_enrolled', 'chapters', 'lessons'
        ]

    def get_instructor_display(self, obj):
        if obj.instructor:
            return obj.instructor.full_name or obj.instructor.phone_number
        return obj.instructor_name or "مدرس آکادمی"

    def get_lessons(self, obj):
        # جهت جلوگیری از کرش فلاتر، تمام جلسات فصل‌ها را در قالب یک لیست صاف هم ارائه می‌دهیم
        all_lessons = Lesson.objects.filter(chapter__course=obj).order_by('chapter__order', 'order')
        return LessonSerializer(all_lessons, many=True, context=self.context).data

    def get_progress_percentage(self, obj):
        user = self.context.get('request') and self.context['request'].user
        if user and user.is_authenticated:
            total_lessons = Lesson.objects.filter(chapter__course=obj).count()
            if total_lessons == 0:
                return 0
            completed = UserProgress.objects.filter(user=user, lesson__chapter__course=obj, is_completed=True).count()
            return int((completed / total_lessons) * 100)
        return 0

    def get_is_enrolled(self, obj):
        user = self.context.get('request') and self.context['request'].user
        if user and user.is_authenticated:
            return CourseEnrollment.objects.filter(user=user, course=obj).exists()
        return False


class MyCourseSerializer(serializers.ModelSerializer):
    progress = serializers.SerializerMethodField()
    modules_text = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    is_completed = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'progress', 'modules_text', 'status', 'is_completed']

    def _calculate_progress(self, obj):
        user = self.context['request'].user
        total_lessons = Lesson.objects.filter(chapter__course=obj).count()
        if total_lessons == 0:
            return 0, 0
        completed_lessons = UserProgress.objects.filter(user=user, lesson__chapter__course=obj, is_completed=True).count()
        return completed_lessons, total_lessons

    def get_progress(self, obj):
        completed, total = self._calculate_progress(obj)
        if total == 0:
            return 0.0
        return round(completed / total, 2)

    def get_modules_text(self, obj):
        completed, total = self._calculate_progress(obj)
        return f"{completed} از {total} جلسه گذرانده شده"

    def get_status(self, obj):
        completed, total = self._calculate_progress(obj)
        if total == 0 or completed == 0:
            return "شروع نشده"
        elif completed == total:
            return "تکمیل شده"
        return "در حال یادگیری"

    def get_is_completed(self, obj):
        completed, total = self._calculate_progress(obj)
        return total > 0 and completed == total


class CertificateSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source='course.title', read_only=True)

    class Meta:
        model = Certificate
        fields = ['id', 'cert_id', 'course_title', 'issued_at', 'image']