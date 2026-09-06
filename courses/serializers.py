from rest_framework import serializers
from .models import Course, Lesson, UserProgress, UserNote

# سریالایزرهای قبلی (بدون تغییر باقی می‌مانند)
class UserNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserNote
        fields = ['id', 'text', 'updated_at']

class LessonSerializer(serializers.ModelSerializer):
    is_completed = serializers.SerializerMethodField()
    user_note = serializers.SerializerMethodField()

    class Meta:
        model = Lesson
        fields = ['id', 'title', 'content', 'video_url', 'order', 'is_completed', 'user_note']

    def get_is_completed(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            if hasattr(obj, 'user_progress'):
                return len(obj.user_progress) > 0
            return UserProgress.objects.filter(user=user, lesson=obj, is_completed=True).exists()
        return False

    def get_user_note(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            if hasattr(obj, 'user_notes'):
                if obj.user_notes:
                    return UserNoteSerializer(obj.user_notes[0]).data
                return None
            note = UserNote.objects.filter(user=user, lesson=obj).first()
            if note:
                return UserNoteSerializer(note).data
        return None

class CourseListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Course
        fields = ['id', 'title', 'thumbnail', 'instructor']

class CourseDetailSerializer(serializers.ModelSerializer):
    lessons = LessonSerializer(many=True, read_only=True)
    progress_percentage = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'thumbnail', 'instructor', 'progress_percentage', 'lessons']

    def get_progress_percentage(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            lessons = obj.lessons.all()
            total_lessons = len(lessons)
            
            if total_lessons == 0:
                return 0
            
            if all(hasattr(l, 'user_progress') for l in lessons):
                completed_lessons = sum(1 for l in lessons if len(l.user_progress) > 0)
            else:
                completed_lessons = UserProgress.objects.filter(user=user, lesson__course=obj, is_completed=True).count()
            
            return int((completed_lessons / total_lessons) * 100)
        return 0


# ==========================================
# سریالایزر جدید برای "دوره‌های من"
# ==========================================
class MyCourseSerializer(serializers.ModelSerializer):
    progress = serializers.SerializerMethodField()
    modules_text = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    is_completed = serializers.SerializerMethodField()

    class Meta:
        model = Course
        # فیلدها دقیقاً منطبق با مدل فلاتر شما تنظیم شده‌اند
        fields = ['id', 'title', 'description', 'progress', 'modules_text', 'status', 'is_completed']

    def _calculate_progress(self, obj):
        """متد کمکی برای محاسبه تعداد کل و تعداد تکمیل شده"""
        lessons = obj.lessons.all()
        total_lessons = len(lessons)
        
        if total_lessons == 0:
            return 0, 0
        
        # از آنجایی که در View از prefetch_related استفاده می‌کنیم، دیتابیس درگیر نمی‌شود
        if all(hasattr(l, 'user_progress') for l in lessons):
            completed_lessons = sum(1 for l in lessons if len(l.user_progress) > 0)
        else:
            # Fallback
            user = self.context['request'].user
            completed_lessons = UserProgress.objects.filter(user=user, lesson__course=obj, is_completed=True).count()
            
        return completed_lessons, total_lessons

    def get_progress(self, obj):
        # فلاتر این عدد را به صورت اعشاری (0.0 تا 1.0) نیاز دارد
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