from rest_framework import serializers
from .models import Exercise, Submission

class ExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = ['id', 'title', 'description', 'starter_code']

class SubmissionSerializer(serializers.ModelSerializer):
    exercise_title = serializers.CharField(source='exercise.title', read_only=True)

    class Meta:
        model = Submission
        fields = ['id', 'exercise', 'exercise_title', 'submitted_code', 'status', 'feedback', 'created_at']
        read_only_fields = ['status', 'feedback'] # کاربر نباید وضعیت را تغییر دهد