from django.db import models

class Banner(models.Model):
    title = models.CharField(max_length=255, verbose_name="عنوان بنر")
    image = models.ImageField(upload_to='banners/', verbose_name="تصویر بنر")
    link = models.URLField(blank=True, null=True, verbose_name="لینک (اختیاری)")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title