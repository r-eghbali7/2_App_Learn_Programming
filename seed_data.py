import os
import django

# تنظیم متغیرهای محیطی برای اجرای اسکریپت خارج از چرخه ریکوئست
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings') # کلمه core را با نام پوشه تنظیمات پروژه خود عوض کنید
django.setup()

from django.contrib.auth import get_user_model
from core.models import Banner
from courses.models import Course, Lesson
from articles.models import Article

User = get_user_model()

def run_seed():
    print("⏳ در حال تزریق داده‌های تستی...")

    # ۱. ساخت کاربر ادمین و تستی
    user, created = User.objects.get_or_create(
        phone_number="09121111111",
        defaults={"full_name": "الکس جانسون", "is_staff": True, "is_superuser": True}
    )
    if created:
        user.set_password("123456")
        user.save()
        print("✅ کاربر تستی ساخته شد (09121111111 - 123456)")

    # ۲. ساخت بنرهای صفحه اصلی
    Banner.objects.get_or_create(title="تسلط بر پایتون در ۳۰ روز", is_active=True)
    Banner.objects.get_or_create(title="تخفیف ویژه دوره‌های معماری", is_active=True)
    print("✅ بنرها ایجاد شدند")

    # ۳. ساخت مقالات
    Article.objects.get_or_create(
        title="آینده هوش مصنوعی در برنامه‌نویسی",
        summary="بررسی نحوه تغییر روند کار روزانه مهندسان نرم‌افزار توسط مدل‌های زبانی بزرگ...",
        content="محتوای کامل مقاله در اینجا قرار می‌گیرد...",
        is_active=True
    )
    Article.objects.get_or_create(
        title="درک معماری گرید CSS",
        summary="ساخت لی‌اوت‌های پیچیده با حداقل کد با استفاده از تکنیک‌های مدرن گرید.",
        content="محتوای کامل مقاله...",
        is_active=True
    )
    print("✅ مقالات ایجاد شدند")

    # ۴. ساخت دوره‌ها و جلسات (ماژول‌ها)
    course1, _ = Course.objects.get_or_create(
        title="الگوهای پیشرفته React",
        description="مدیریت وضعیت پیچیده، هوک‌های سفارشی و بهینه‌سازی عملکرد در برنامه‌های React.",
        instructor="دکتر سارا شفیعی",
        is_active=True
    )
    
    # ۴. ساخت دوره‌ها و جلسات (ماژول‌ها)
    course1, _ = Course.objects.get_or_create(
        title="الگوهای پیشرفته React",
        defaults={
            "description": "مدیریت وضعیت پیچیده، هوک‌های سفارشی و بهینه‌سازی عملکرد در برنامه‌های React.",
            "instructor": "دکتر سارا شفیعی",
            "is_active": True
        }
    )
    
    Lesson.objects.get_or_create(
        course=course1, 
        title="مقدمه‌ای بر کامپوننت‌ها", 
        defaults={"order": 1, "video_url": "https://example.com/vid1.mp4"}
    )
    Lesson.objects.get_or_create(
        course=course1, 
        title="مدیریت State", 
        defaults={"order": 2, "video_url": "https://example.com/vid2.mp4"}
    )

    course2, _ = Course.objects.get_or_create(
        title="معماری میکروسرویس‌ها",
        defaults={
            "description": "بررسی عمیق تجزیه برنامه‌های یکپارچه به میکروسرویس‌های مقاوم و مقیاس‌پذیر.",
            "instructor": "مهندس امیر محمدی",
            "is_active": True
        }
    )
    print("✅ دوره‌ها و جلسات ایجاد شدند")

    print("🎉 تمام داده‌های تستی با موفقیت به دیتابیس SQLite اضافه شدند!")

if __name__ == '__main__':
    run_seed()