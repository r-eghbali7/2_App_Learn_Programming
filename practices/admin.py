from django.contrib import admin
from .models import Exercise, Submission

@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_active']
    search_fields = ['title']

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['user', 'exercise', 'status', 'created_at']
    list_filter = ['status', 'exercise']
    search_fields = ['user__phone_number']
    list_editable = ['status']