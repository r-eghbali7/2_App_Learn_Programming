# practices/serializers.py
from rest_framework import serializers
from .models import Exercise, Submission

class ExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = ['id', 'title', 'description', 'starter_code', 'language', 'is_active']

class SubmissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Submission
        fields = ['id', 'exercise', 'submitted_code', 'status', 'feedback', 'created_at']
        # این فیلدها نباید توسط فلاتر اجباری فرستاده شوند چون در بک‌اند مقداردهی می‌شوند
        read_only_fields = ['status', 'feedback', 'user', 'created_at']