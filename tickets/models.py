from django.db import models
from django.conf import settings

class Ticket(models.Model):
    STATUS_CHOICES = (
        ('pending', 'در انتظار پاسخ'),
        ('open', 'پاسخ داده شده'),
        ('closed', 'بسته شده'),
    )
    SUBJECT_CHOICES = (
        ('technical', 'پشتیبانی فنی'),
        ('financial', 'امور مالی و خرید'),
        ('educational', 'سوالات آموزشی'),
        ('other', 'سایر موارد'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tickets')
    subject = models.CharField(max_length=20, choices=SUBJECT_CHOICES, verbose_name="موضوع")
    message = models.TextField(verbose_name="متن پیام")
    attachment = models.FileField(upload_to='tickets/attachments/', null=True, blank=True, verbose_name="فایل ضمیمه")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="وضعیت")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"تیکت {self.user.phone_number} - {self.get_subject_display()}"