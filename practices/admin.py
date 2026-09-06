from django.contrib import admin
from .models import Exercise, Submission

@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    # فرض بر این است که فیلد language را به مدل Exercise اضافه کرده‌اید
    list_display = ['title', 'language', 'is_active'] 
    list_editable = ['is_active']
    list_filter = ['language', 'is_active']
    search_fields = ['title', 'description']

@admin.register(Submission)
class SubmissionAdmin(admin.ModelAdmin):
    list_display = ['user', 'exercise', 'status', 'created_at']
    list_filter = ['status', 'exercise']
    search_fields = ['user__phone_number']
    readonly_fields = ['user', 'exercise', 'submitted_code', 'created_at'] # بهتر است کدهای ارسالی تغییر نکنند