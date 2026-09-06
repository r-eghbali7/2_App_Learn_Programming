# core/utils.py
import jdatetime

def convert_to_shamsi(date_obj, include_time=False):
    """
    دریافت یک شیء datetime (میلادی) و تبدیل آن به رشته شمسی (فارسی).
    اگر date_obj خالی باشد، یک رشته خالی برمی‌گرداند.
    """
    if not date_obj:
        return ""
    
    # اول مطمئن می‌شویم که تاریخ به تایم‌زون محلی (تهران) تبدیل شده باشد
    from django.utils.timezone import localtime
    local_time = localtime(date_obj)

    # تبدیل به تقویم جلالی
    jalali_date = jdatetime.datetime.fromgregorian(datetime=local_time)
    
    # تغییر نام ماه‌ها به فارسی برای زیبایی بیشتر (این پکیج به صورت پیش‌فرض فارسی است اما برای اطمینان)
    jalali_date.locale = 'fa_IR'
    
    if include_time:
        # خروجی: ۱۵ شهریور ۱۴۰۵، ۱۸:۳۰
        return jalali_date.strftime('%d %B %Y، %H:%M')
    else:
        # خروجی: ۱۵ شهریور ۱۴۰۵
        return jalali_date.strftime('%d %B %Y')