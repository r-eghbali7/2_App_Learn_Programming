# courses/models.py
from django.db import models
from django.conf import settings

class Course(models.Model):
    title = models.CharField(max_length=255, verbose_name="عنوان دوره")
    description = models.TextField(verbose_name="توضیحات")
    thumbnail = models.ImageField(upload_to='courses/thumbnails/', null=True, blank=True, verbose_name="تصویر دوره")
    instructor = models.CharField(max_length=150, verbose_name="مدرس")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Lesson(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='lessons', verbose_name="دوره")
    title = models.CharField(max_length=255, verbose_name="عنوان جلسه")
    content = models.TextField(blank=True, null=True, verbose_name="متن توضیحات جلسه")
    video_url = models.URLField(max_length=500, blank=True, null=True, verbose_name="لینک ویدیو")
    order = models.PositiveIntegerField(default=0, verbose_name="ترتیب نمایش")

    class Meta:
        ordering = ['order']

    def __str__(self):
        return f"{self.course.title} - {self.title}"

class UserProgress(models.Model):
    """برای محاسبه درصد پیشرفت دوره"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='progress')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='completed_by')
    is_completed = models.BooleanField(default=True)
    completed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'lesson')

class UserNote(models.Model):
    """برای قسمت یادداشت مطلب شخصی آموزشی"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notes')
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='notes')
    text = models.TextField(verbose_name="متن یادداشت")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('user', 'lesson') # هر کاربر برای هر جلسه یک فضا برای یادداشت دارد