from django.db import models

class Article(models.Model):
    title = models.CharField(max_length=255, verbose_name="عنوان مقاله")
    summary = models.TextField(verbose_name="خلاصه مقاله") # برای نمایش در لیست
    content = models.TextField(verbose_name="متن کامل")
    image = models.ImageField(upload_to='articles/images/', null=True, blank=True, verbose_name="تصویر مقاله")
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at'] # جدیدترین‌ها در ابتدا

    def __str__(self):
        return self.title