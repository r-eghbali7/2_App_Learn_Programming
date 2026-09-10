# courses/models.py
import uuid
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class Course(models.Model):
    """مدل اصلی دوره آموزشی"""
    title = models.CharField(max_length=255, verbose_name="عنوان دوره")
    slug = models.SlugField(max_length=255, unique=True, allow_unicode=True, blank=True, null=True, verbose_name="اسلاگ URL")
    description = models.TextField(verbose_name="توضیحات دوره")
    thumbnail = models.ImageField(upload_to='courses/thumbnails/', null=True, blank=True, verbose_name="تصویر دوره")
    
    # مدرس به عنوان ارتباط با مدل User (جهت تفکیک دسترسی و پنل مدرس)
    instructor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='instructors_courses',
        verbose_name="مدرس دوره"
    )
    instructor_name = models.CharField(max_length=150, blank=True, verbose_name="نام نمایشی مدرس")

    price = models.PositiveIntegerField(default=0, verbose_name="قیمت نقدی (تومان)")
    is_free = models.BooleanField(default=False, verbose_name="رایگان؟")
    requires_vip = models.BooleanField(default=True, verbose_name="دسترسی با اشتراک ویژه؟")
    is_active = models.BooleanField(default=True, verbose_name="وضعیت انتشار")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخرین بروزرسانی")

    class Meta:
        verbose_name = "دوره"
        verbose_name_plural = "دوره‌ها"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    @property
    def total_lessons_count(self):
        return Lesson.objects.filter(chapter__course=self).count()


class Chapter(models.Model):
    """سرفصل‌های هر دوره جهت سازمان‌دهی دروس و آزمون‌های پایان فصل"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='chapters', verbose_name="دوره")
    title = models.CharField(max_length=200, verbose_name="عنوان سرفصل / فصل")
    order = models.PositiveIntegerField(default=1, verbose_name="شماره ترتیب")

    class Meta:
        verbose_name = "فصل"
        verbose_name_plural = "فصل‌ها"
        ordering = ['order']

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Lesson(models.Model):
    """جلسات آموزشی هر فصل"""
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE, related_name='lessons', verbose_name="فصل")
    title = models.CharField(max_length=255, verbose_name="عنوان جلسه")
    content = models.TextField(blank=True, null=True, verbose_name="متن و توضیحات تکمیلی")
    video_url = models.URLField(max_length=500, blank=True, null=True, verbose_name="لینک ویدیو (استریم/دانلودی)")
    duration_minutes = models.PositiveIntegerField(default=0, verbose_name="مدت زمان (دقیقه)")
    order = models.PositiveIntegerField(default=1, verbose_name="ترتیب نمایش در فصل")
    is_free_preview = models.BooleanField(default=False, verbose_name="پیش‌نمایش رایگان؟ (مشاهده بدون خرید)")

    class Meta:
        verbose_name = "جلسه"
        verbose_name_plural = "جلسات"
        ordering = ['order']

    def __str__(self):
        return f"{self.chapter.title} - {self.title}"

    @property
    def course(self):
        return self.chapter.course


class CourseEnrollment(models.Model):
    """ثبت خرید تکی دوره توسط دانشجو"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='enrollments', verbose_name="دانشجو")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments', verbose_name="دوره")
    amount_paid = models.PositiveIntegerField(default=0, verbose_name="مبلغ پرداختی (تومان)")
    purchased_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ خرید")

    class Meta:
        verbose_name = "ثبت‌نام دوره"
        verbose_name_plural = "ثبت‌نام‌های دوره‌ها"
        unique_together = ('user', 'course')

    def __str__(self):
        return f"{self.user} -> {self.course.title}"


class UserProgress(models.Model):
    """ردگیری پیشرفت و مشاهده جلسات توسط دانشجو"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='progress', verbose_name="کاربر")
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='completed_by', verbose_name="جلسه")
    is_completed = models.BooleanField(default=True, verbose_name="تکمیل شده؟")
    completed_at = models.DateTimeField(auto_now_add=True, verbose_name="زمان تکمیل")

    class Meta:
        verbose_name = "پیشرفت کاربر"
        verbose_name_plural = "پیشرفت‌های کاربران"
        unique_together = ('user', 'lesson')


class UserNote(models.Model):
    """یادداشت‌های شخصی دانشجو هنگام تماشای ویدیو"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='notes', verbose_name="کاربر")
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='notes', verbose_name="جلسه")
    text = models.TextField(verbose_name="متن یادداشت")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ ثبت")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="آخرین ویرایش")

    class Meta:
        verbose_name = "یادداشت درس"
        verbose_name_plural = "یادداشت‌های دروس"
        unique_together = ('user', 'lesson')


class Certificate(models.Model):
    """گواهینامه پایان دوره با شماره سریال یکتا"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='certificates', verbose_name="کاربر")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='certificates', verbose_name="دوره")
    cert_id = models.CharField(max_length=30, unique=True, db_index=True, verbose_name="شماره سریال مدرک")
    image = models.ImageField(upload_to='certificates/issued/', blank=True, null=True, verbose_name="تصویر نهایی مدرک")
    issued_at = models.DateTimeField(auto_now_add=True, verbose_name="تاریخ صدور")

    class Meta:
        verbose_name = "گواهینامه"
        verbose_name_plural = "گواهینامه‌ها"
        unique_together = ('user', 'course')

    def save(self, *args, **kwargs):
        if not self.cert_id:
            self.cert_id = f"CG-{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.cert_id} | {self.user} - {self.course.title}"


# ========================================================
# سیستم آزمون آنلاین (Online Quiz System)
# ========================================================

class Quiz(models.Model):
    """آزمون آنلاین که می‌تواند متعلق به یک سرفصل مشخص یا کل دوره باشد"""
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='quizzes', verbose_name="دوره")
    chapter = models.ForeignKey(Chapter, on_delete=models.SET_NULL, null=True, blank=True, related_name='quizzes', verbose_name="مربوط به فصل (اختیاری)")
    title = models.CharField(max_length=200, verbose_name="عنوان آزمون")
    description = models.TextField(blank=True, null=True, verbose_name="توضیحات یا راهنمای آزمون")
    pass_score = models.PositiveIntegerField(default=70, validators=[MinValueValidator(1), MaxValueValidator(100)], verbose_name="حداقل نمره قبولی (درصد)")
    time_limit_minutes = models.PositiveIntegerField(default=15, verbose_name="مدت زمان آزمون (دقیقه)")
    is_active = models.BooleanField(default=True, verbose_name="فعال؟")

    class Meta:
        verbose_name = "آزمون آنلاین"
        verbose_name_plural = "آزمون‌های آنلاین"

    def __str__(self):
        return f"{self.course.title} - {self.title}"


class Question(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions', verbose_name="آزمون")
    text = models.TextField(verbose_name="متن سوال")
    explanation = models.TextField(blank=True, null=True, verbose_name="توضیح پاسخ (بعد از آزمون)")
    order = models.PositiveIntegerField(default=1, verbose_name="ترتیب سوال")

    class Meta:
        verbose_name = "سوال آزمون"
        verbose_name_plural = "سوالات آزمون"
        ordering = ['order']

    def __str__(self):
        return f"سوال {self.order}: {self.text[:50]}"


class Option(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options', verbose_name="سوال")
    text = models.CharField(max_length=300, verbose_name="متن گزینه")
    is_correct = models.BooleanField(default=False, verbose_name="گزینه صحیح است؟")

    class Meta:
        verbose_name = "گزینه"
        verbose_name_plural = "گزینه‌های سوال"

    def __str__(self):
        return f"{self.text} {'(صحیح)' if self.is_correct else ''}"


class QuizResult(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='quiz_results', verbose_name="کاربر")
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='results', verbose_name="آزمون")
    score = models.PositiveIntegerField(verbose_name="نمره کسب شده (درصد)")
    passed = models.BooleanField(default=False, verbose_name="قبول شده؟")
    attempt_number = models.PositiveIntegerField(default=1, verbose_name="نوبت تلاش")
    completed_at = models.DateTimeField(auto_now_add=True, verbose_name="زمان اتمام")

    class Meta:
        verbose_name = "نتیجه آزمون"
        verbose_name_plural = "نتایج آزمون‌ها"
        ordering = ['-completed_at']

    def __str__(self):
        return f"{self.user} - {self.quiz.title} ({self.score}%)"


# ========================================================
# سیستم پرسش و پاسخ دانشجویان (Q&A)
# ========================================================

class LessonQuestion(models.Model):
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='questions', verbose_name="جلسه")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='asked_questions', verbose_name="کاربر")
    title = models.CharField(max_length=200, verbose_name="موضوع سوال")
    content = models.TextField(verbose_name="متن پرسش")
    is_resolved = models.BooleanField(default=False, verbose_name="حل شده؟")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="زمان ارسال")

    class Meta:
        verbose_name = "پرسش دانشجو"
        verbose_name_plural = "پرسش‌های دانشجویان"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.user})"


class LessonAnswer(models.Model):
    question = models.ForeignKey(LessonQuestion, on_delete=models.CASCADE, related_name='answers', verbose_name="پرسش مربوطه")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='given_answers', verbose_name="پاسخ‌دهنده")
    content = models.TextField(verbose_name="متن پاسخ")
    is_instructor_answer = models.BooleanField(default=False, verbose_name="پاسخ استاد؟")
    is_accepted = models.BooleanField(default=False, verbose_name="پاسخ برگزیده / تایید شده")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="زمان ارسال")

    class Meta:
        verbose_name = "پاسخ پرسش"
        verbose_name_plural = "پاسخ‌های پرسش‌ها"
        ordering = ['created_at']

    def __str__(self):
        return f"پاسخ توسط {self.user} به {self.question.title}"