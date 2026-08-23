# courses/serializers.py
from rest_framework import serializers
from .models import Course, Lesson, UserProgress, UserNote

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
            return UserProgress.objects.filter(user=user, lesson=obj, is_completed=True).exists()
        return False

    def get_user_note(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            note = UserNote.objects.filter(user=user, lesson=obj).first()
            if note:
                return UserNoteSerializer(note).data
        return None

class CourseListSerializer(serializers.ModelSerializer):
    """برای نمایش در صفحه اول و لیست دوره‌ها (خلاصه)"""
    class Meta:
        model = Course
        fields = ['id', 'title', 'thumbnail', 'instructor']

class CourseDetailSerializer(serializers.ModelSerializer):
    """برای صفحه جزئیات دوره به همراه لیست جلسات و محاسبه پروگرس بار"""
    lessons = LessonSerializer(many=True, read_only=True)
    progress_percentage = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ['id', 'title', 'description', 'thumbnail', 'instructor', 'progress_percentage', 'lessons']

    def get_progress_percentage(self, obj):
        user = self.context['request'].user
        if user.is_authenticated:
            total_lessons = obj.lessons.count()
            if total_lessons == 0:
                return 0
            completed_lessons = UserProgress.objects.filter(user=user, lesson__course=obj, is_completed=True).count()
            return int((completed_lessons / total_lessons) * 100)
        return 0