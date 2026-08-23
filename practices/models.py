from django.db import models
from django.conf import settings

class Exercise(models.Model):
    title = models.CharField(max_length=255, verbose_name="عنوان تمرین")
    description = models.TextField(verbose_name="صورت مسئله")
    starter_code = models.TextField(blank=True, null=True, verbose_name="کد اولیه (استارتر)")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title

class Submission(models.Model):
    STATUS_CHOICES = (
        ('pending', 'در حال بررسی'),
        ('passed', 'تایید شده'),
        ('failed', 'رد شده'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='submissions')
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name='submissions')
    submitted_code = models.TextField(verbose_name="کد ارسالی کاربر")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    feedback = models.TextField(blank=True, null=True, verbose_name="بازخورد یا خطای سیستم")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.phone_number} - {self.exercise.title} ({self.status})"