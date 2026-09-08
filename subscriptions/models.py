from django.db import models
from django.conf import settings
from datetime import timedelta
from django.utils import timezone

class Plan(models.Model):
    title = models.CharField(max_length=100, verbose_name="نام پلن")
    duration_days = models.PositiveIntegerField(verbose_name="مدت زمان (روز)")
    price = models.PositiveIntegerField(verbose_name="قیمت (تومان)")
    description = models.TextField(blank=True, null=True, verbose_name="توضیحات")
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['id']
        
    def __str__(self):
        return self.title

class UserSubscription(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True)
    start_date = models.DateTimeField(auto_now_add=True)
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        if not self.end_date and self.plan:
            # محاسبه خودکار تاریخ پایان بر اساس روزهای پلن
            self.end_date = timezone.now() + timedelta(days=self.plan.duration_days)
        super().save(*args, **kwargs)

    @property
    def is_valid(self):
        return self.is_active and self.end_date > timezone.now()

    def __str__(self):
        return f"{self.user.phone_number} - {self.plan.title}"


# کدهای قبلی سر جای خود بمانند...

class Transaction(models.Model):
    STATUS_CHOICES = (
        ('pending', 'در حال انتظار'),
        ('success', 'موفق'),
        ('failed', 'ناموفق'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='transactions', verbose_name='کاربر')
    plan = models.ForeignKey(Plan, on_delete=models.SET_NULL, null=True, verbose_name='پلن خریداری شده')
    authority = models.CharField(max_length=100, unique=True, verbose_name='کد اتوریتی زرین‌پال')
    ref_id = models.CharField(max_length=100, blank=True, null=True, verbose_name='کد پیگیری تراکنش')
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='مبلغ (تومان)')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name='وضعیت تراکنش')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='تاریخ ایجاد')

    def __str__(self):
        return f"{self.user.phone_number} - {self.plan.title if self.plan else 'حذف شده'} - {self.status}"