# courses/tests.py
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from .models import Course, Lesson, UserProgress, UserNote

User = get_user_model()

class CourseAPITests(APITestCase):
    def setUp(self):
        # ساخت کاربر تستی
        self.user = User.objects.create_user(phone_number="09123456789", password="testpass")
        
        # ساخت دوره تستی
        self.course = Course.objects.create(
            title="آموزش فلاتر",
            description="دوره جامع فلاتر",
            instructor="استاد تست",
            is_active=True
        )
        
        # ساخت دو جلسه برای دوره
        self.lesson1 = Lesson.objects.create(course=self.course, title="نصب فلاتر", order=1)
        self.lesson2 = Lesson.objects.create(course=self.course, title="ویجت‌ها", order=2)

        # URL های مربوط به ViewSet ها
        # نام‌گذاری‌ها بر اساس router.register انجام می‌شود
        self.course_list_url = reverse('course-list')
        self.course_detail_url = reverse('course-detail', args=[self.course.id])
        self.toggle_complete_url = reverse('lesson-action-toggle-complete', args=[self.lesson1.id])
        self.note_url = reverse('lesson-action-manage-note', args=[self.lesson1.id])

    def test_get_course_list(self):
        response = self.client.get(self.course_list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], "آموزش فلاتر")

    def test_get_course_detail_and_progress(self):
        # لاگین کردن کاربر
        self.client.force_authenticate(user=self.user)
        
        # کاربر درس اول را تمام کرده است (50% پیشرفت)
        UserProgress.objects.create(user=self.user, lesson=self.lesson1, is_completed=True)
        
        response = self.client.get(self.course_detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['progress_percentage'], 50)
        self.assertEqual(len(response.data['lessons']), 2)
        
        # بررسی اینکه وضعیت is_completed برای درس اول در خروجی True باشد
        lesson1_data = next(item for item in response.data['lessons'] if item["id"] == self.lesson1.id)
        self.assertTrue(lesson1_data['is_completed'])

    def test_toggle_lesson_complete(self):
        self.client.force_authenticate(user=self.user)
        
        # درخواست اول: تیک خوردن ویدیو
        response = self.client.post(self.toggle_complete_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_completed'])
        self.assertTrue(UserProgress.objects.filter(user=self.user, lesson=self.lesson1, is_completed=True).exists())
        
        # درخواست دوم: برداشتن تیک ویدیو
        response = self.client.post(self.toggle_complete_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['is_completed'])
        self.assertTrue(UserProgress.objects.filter(user=self.user, lesson=self.lesson1, is_completed=False).exists())

    def test_manage_user_note(self):
        self.client.force_authenticate(user=self.user)
        
        # تست ایجاد یادداشت جدید
        post_data = {'text': 'این یک یادداشت مهم برای نصب فلاتر است.'}
        response = self.client.post(self.note_url, post_data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'success')
        self.assertTrue(UserNote.objects.filter(user=self.user, lesson=self.lesson1).exists())
        
        # تست دریافت یادداشت نوشته شده
        response = self.client.get(self.note_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['text'], 'این یک یادداشت مهم برای نصب فلاتر است.')