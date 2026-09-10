import os
import django
from datetime import timedelta

# تنظیم متغیرهای محیطی برای اجرای اسکریپت خارج از سرور
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.utils import timezone
from django.contrib.auth import get_user_model
from core.models import Banner
from articles.models import Article
from courses.models import (
    Course, Chapter, Lesson, CourseEnrollment,
    UserProgress, UserNote, Certificate,
    Quiz, Question, Option
)
from practices.models import Exercise, Submission
from subscriptions.models import Plan, UserSubscription, Transaction
from tickets.models import Ticket

User = get_user_model()

def run_seed():
    print("🚀 در حال آماده‌سازی و تزریق داده‌های تستی جامع برای اپلیکیشن فلاتر...")

    # ۱. کاربر تستی اصلی (دانشجو و مدیر)
    test_user, created = User.objects.get_or_create(
        phone_number="09121111111",
        defaults={
            "full_name": "امیررضا رضایی",
            "is_staff": True,
            "is_superuser": True,
            "is_active": True
        }
    )
    test_user.set_password("123456")
    test_user.save()
    print("✅ کاربر تست ساخته/به‌روز شد: شماره: 09121111111 | رمز: 123456")

    # مدرس تستی
    instructor_user, _ = User.objects.get_or_create(
        phone_number="09122222222",
        defaults={
            "full_name": "دکتر سارا شفیعی",
            "is_staff": True,
            "is_active": True
        }
    )
    instructor_user.set_password("123456")
    instructor_user.save()

    # ۲. بنرهای اسلایدر صفحه اصلی (Home)
    banners_data = [
        {"title": "تخفیف ویژه اشتراک سالانه آکادمی", "link": "https://example.com/discount"},
        {"title": "مسیر جامع یادگیری جنگو و فلاتر ۲۰۲۶", "link": "https://example.com/roadmap"},
        {"title": "ورود به دنیای هوش مصنوعی و مدل‌های زبانی", "link": "https://example.com/ai"},
    ]
    for b in banners_data:
        Banner.objects.get_or_create(title=b["title"], defaults={"link": b["link"], "is_active": True})
    print("✅ بنرهای اسلایدر صفحه اصلی اضافه شدند.")

    # ۳. مقالات آموزشی (Articles)
    articles_data = [
        {
            "title": "راهنمای کامل مدیریت وضعیت با GetX در فلاتر",
            "summary": "بررسی روش‌های مختلف مدیریت State و مسیریابی سریع در فلاتر بدون Boilerplateهای اضافه.",
            "content": "فلاتر فریم‌ورکی منعطف است و کتابخانه GetX یکی از محبوب‌ترین ابزارها برای کنترل وضعیت، تزریق وابستگی و مسیریابی ساده است...",
        },
        {
            "title": "بهینه‌سازی دیتابیس در Django با select_related و prefetch_related",
            "summary": "چگونه کوئری‌های N+1 را شناسایی کرده و سرعت پاسخ‌دهی APIهای رست را تا ۱۰ برابر افزایش دهیم.",
            "content": "یکی از بزرگترین چالش‌ها در برنامه‌های جنگو، لود کردن داده‌های مرتبط در لوپ‌ها است که فشار سنگینی به سرور وارد می‌کند...",
        },
        {
            "title": "آینده توسعه نرم‌افزار با هوش مصنوعی و مدل‌های محلی",
            "summary": "نحوه ادغام مدل‌های هوش مصنوعی با اپلیکیشن‌های موبایل جهت هوشمندسازی دستیار شخصی.",
            "content": "توسعه‌دهندگان امروزه با استفاده از APIهای ابری و مدل‌های سبک روی دستگاه می‌توانند قابلیت‌های بی‌نظیری خلق کنند...",
        }
    ]
    for art in articles_data:
        Article.objects.get_or_create(
            title=art["title"],
            defaults={"summary": art["summary"], "content": art["content"], "is_active": True}
        )
    print("✅ مقالات آموزشی ثبت شدند.")

    # ۴. پلن‌های اشتراک ویژه و فعال‌سازی برای کاربر تست
    plan_monthly, _ = Plan.objects.get_or_create(
        title="اشتراک برنزی (۱ ماهه)",
        defaults={"duration_days": 30, "price": 199000, "description": "دسترسی نامحدود به تمامی دوره‌ها به مدت یک ماه"}
    )
    plan_quarterly, _ = Plan.objects.get_or_create(
        title="اشتراک نقره‌ای (۳ ماهه)",
        defaults={"duration_days": 90, "price": 490000, "description": "دسترسی کامل ۳ ماهه به همراه وبینارهای ماهانه"}
    )
    plan_yearly, _ = Plan.objects.get_or_create(
        title="اشتراک طلایی ویژه (۱ ساله)",
        defaults={"duration_days": 365, "price": 1490000, "description": "دسترسی نامحدود سالانه به همراه دریافت مدارک رایگان"}
    )

    # فعال کردن یک اشتراک فعال ۳۰ روزه برای کاربر تست
    UserSubscription.objects.filter(user=test_user).delete()
    UserSubscription.objects.create(
        user=test_user,
        plan=plan_monthly,
        start_date=timezone.now(),
        end_date=timezone.now() + timedelta(days=28),
        is_active=True
    )

    # ایجاد یک تراکنش موفق و یک تراکنش ناموفق در سابقه خریدها
    Transaction.objects.get_or_create(
        authority="A00000000000000000000000000012345678",
        defaults={
            "user": test_user,
            "plan": plan_monthly,
            "amount": plan_monthly.price,
            "ref_id": "987654321",
            "status": "success"
        }
    )
    Transaction.objects.get_or_create(
        authority="A00000000000000000000000000087654321",
        defaults={
            "user": test_user,
            "plan": plan_quarterly,
            "amount": plan_quarterly.price,
            "ref_id": None,
            "status": "failed"
        }
    )
    print("✅ پلن‌ها، اشتراک فعال کاربر و سابقه خریدها آماده شدند.")

    # ۵. دوره‌ها، فصل‌ها و جلسات آموزشی (Courses, Chapters, Lessons)
    course1, _ = Course.objects.get_or_create(
        title="دوره جامع و تخصصی فلاتر (Flutter Pro)",
        defaults={
            "description": "از مفاهیم پایه ویجت‌ها تا معماری Clean و اتصال به وب‌سرویس‌های RESTful با پروژه‌های واقعی.",
            "instructor": instructor_user,
            "instructor_name": "دکتر سارا شفیعی",
            "price": 650000,
            "is_free": False,
            "requires_vip": True,
            "is_active": True
        }
    )

    # فصل اول دوره فلاتر
    ch1, _ = Chapter.objects.get_or_create(course=course1, title="فصل ۱: راه‌اندازی و معماری پایه", defaults={"order": 1})
    l1, _ = Lesson.objects.get_or_create(
        chapter=ch1,
        title="مقدمه و نصب ابزارهای توسعه فلاتر",
        defaults={
            "content": "در این جلسه با سیستم‌عامل، نیازمندی‌ها و تنظیمات اولیه Android Studio و VS Code آشنا می‌شویم.",
            "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4",
            "duration_minutes": 15,
            "order": 1,
            "is_free_preview": True
        }
    )
    l2, _ = Lesson.objects.get_or_create(
        chapter=ch1,
        title="آشنایی عمیق با چرخه حیات ویجت‌ها",
        defaults={
            "content": "تفاوت Stateless و Stateful Widget و درک متدهای initState و dispose.",
            "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4",
            "duration_minutes": 22,
            "order": 2,
            "is_free_preview": False
        }
    )

    # فصل دوم دوره فلاتر
    ch2, _ = Chapter.objects.get_or_create(course=course1, title="فصل ۲: شبکه و وب‌سرویس‌ها", defaults={"order": 2})
    l3, _ = Lesson.objects.get_or_create(
        chapter=ch2,
        title="ارتباط با سرور به کمک پکیج Dio و هندل ارورها",
        defaults={
            "content": "نحوه راه‌اندازی Interceptor برای توکن‌های JWT و ارسال هدرهای احراز هویت.",
            "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4",
            "duration_minutes": 30,
            "order": 1,
            "is_free_preview": False
        }
    )

    # دوره دوم (رایگان)
    course2, _ = Course.objects.get_or_create(
        title="مبانی برنامه‌نویسی پایتون برای مبتدیان",
        defaults={
            "description": "آموزش مقدماتی ساختار داده‌ها، توابع و شی‌گرایی در زبان پایتون.",
            "instructor": instructor_user,
            "instructor_name": "مهندس رضا کریمی",
            "price": 0,
            "is_free": True,
            "requires_vip": False,
            "is_active": True
        }
    )
    ch_py, _ = Chapter.objects.get_or_create(course=course2, title="فصل ۱: متغیرها و انواع داده", defaults={"order": 1})
    l_py1, _ = Lesson.objects.get_or_create(
        chapter=ch_py,
        title="انواع داده عددی و رشته‌ها در پایتون",
        defaults={
            "content": "تعریف متغیر، قوانین نام‌گذاری و کار با استرینگ‌ها.",
            "video_url": "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerEscapes.mp4",
            "duration_minutes": 18,
            "order": 1,
            "is_free_preview": True
        }
    )

    # ۶. ثبت‌نام دوره، پیشرفت و یادداشت کاربر تستی
    CourseEnrollment.objects.get_or_create(user=test_user, course=course1, defaults={"amount_paid": 650000})
    
    # تیک زدن جلسات اول و دوم به عنوان تکمیل‌شده (جهت تست درصد پیشرفت در اپلیکیشن)
    UserProgress.objects.get_or_create(user=test_user, lesson=l1, defaults={"is_completed": True})
    UserProgress.objects.get_or_create(user=test_user, lesson=l2, defaults={"is_completed": True})

    # ثبت یک یادداشت نمونه برای جلسه ۱
    UserNote.objects.update_or_create(
        user=test_user,
        lesson=l1,
        defaults={"text": "نکته کلیدی: حتماً متغیر ANDROID_HOME را در مسیر environment سیستم ست کنید."}
    )

    # ۷. صدور یک مدرک تستی (Certificate) برای کاربر
    Certificate.objects.get_or_create(
        user=test_user,
        course=course2,
        defaults={"cert_id": "CG-98A1F4C2"}
    )
    print("✅ دوره‌ها، سرفصل‌ها، پیشرفت و گواهینامه برای کاربر ثبت شدند.")

    # ۸. تمرین‌های کد ادیتور آنلاین (Practices / Code Editor)
    ex1, _ = Exercise.objects.get_or_create(
        title="محاسبه مجموع اعداد زوج یک لیست",
        defaults={
            "description": "تابعی بنویسید که لیستی از اعداد را گرفته و فقط مجموع اعداد زوج را چاپ کند.",
            "starter_code": "def sum_even_numbers(numbers):\n    # کد خود را اینجا بنویسید\n    pass\n\nprint(sum_even_numbers([1, 2, 3, 4, 5, 6]))",
            "language": "Python",
            "is_active": True
        }
    )
    ex2, _ = Exercise.objects.get_or_create(
        title="معکوس کردن رشته در جاوااسکریپت",
        defaults={
            "description": "تابعی بنویسید که یک رشته متنی را دریافت کرده و معکوس آن را در خروجی لاگ کند.",
            "starter_code": "function reverseString(str) {\n    // کد شما اینجا\n    return str.split('').reverse().join('');\n}\n\nconsole.log(reverseString('CodeGlass'));",
            "language": "JS",
            "is_active": True
        }
    )
    Submission.objects.get_or_create(
        user=test_user,
        exercise=ex1,
        defaults={
            "submitted_code": "def sum_even_numbers(numbers):\n    return sum(x for x in numbers if x % 2 == 0)\nprint(sum_even_numbers([1, 2, 3, 4, 5, 6]))",
            "status": "passed",
            "feedback": "خروجی برنامه:\n12\n\nتست‌ها با موفقیت پاس شدند."
        }
    )
    print("✅ تمرین‌های کدنویسی آنلاین افزوده شدند.")

    # ۹. تیکت‌های پشتیبانی (Tickets)
    ticket_data = [
        {
            "subject": "financial",
            "message": "سلام، مبلغ اشتراک از حساب من کسر شد اما وضعیت اشتراک در اپلیکیشن فعال نشده بود که البته الان حل شد.",
            "status": "closed"
        },
        {
            "subject": "educational",
            "message": "در جلسه ۳ دوره فلاتر، خطای DioException نوع Bad Certificate دریافت می‌کنم، چطور حل کنم؟",
            "status": "open"
        },
        {
            "subject": "technical",
            "message": "آیا امکان دارد در ادیتور آنلاین تم روشن (Light) هم اضافه شود؟",
            "status": "pending"
        }
    ]
    for t in ticket_data:
        Ticket.objects.get_or_create(
            user=test_user,
            subject=t["subject"],
            message=t["message"],
            defaults={"status": t["status"]}
        )
    print("✅ تیکت‌های پشتیبانی کاربر ایجاد شدند.")

    print("\n🎉 تمام داده‌های تستی با موفقیت در دیتابیس درج شدند!")
    print("--------------------------------------------------")
    print("📌 مشخصات ورود به اپلیکیشن فلاتر:")
    print("📱 شماره موبایل: 09121111111")
    print("🔑 رمز عبور: 123456")
    print("🌟 وضعیت: دارای اشتراک VIP، دوره‌های فعال، سوابق خرید و تیکت")
    print("--------------------------------------------------")

if __name__ == '__main__':
    run_seed()