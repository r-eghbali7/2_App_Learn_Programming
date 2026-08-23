# practices/tests.py
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from .models import Exercise, Submission

User = get_user_model()

class PracticeAPITests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(phone_number="09121111111", password="testpass1")
        self.user2 = User.objects.create_user(phone_number="09122222222", password="testpass2")
        
        self.exercise = Exercise.objects.create(
            title="تمرین حلقه For",
            description="یک حلقه بنویسید که اعداد 1 تا 10 را چاپ کند.",
            starter_code="for i in range(10):"
        )
        
        self.exercises_url = reverse('exercise-list')
        self.submissions_url = reverse('submission-list')

    def test_unauthenticated_access(self):
        # کاربری که لاگین نکرده نباید به تمرین‌ها دسترسی داشته باشد
        response = self.client.get(self.exercises_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_exercises_list(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.exercises_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], "تمرین حلقه For")

    def test_create_submission(self):
        self.client.force_authenticate(user=self.user1)
        
        data = {
            'exercise': self.exercise.id,
            'submitted_code': "for i in range(1, 11):\n    print(i)"
        }
        response = self.client.post(self.submissions_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['status'], 'pending') # پیش‌فرض باید pending باشد
        
        # بررسی در دیتابیس
        submission = Submission.objects.get(id=response.data['id'])
        self.assertEqual(submission.user, self.user1)

    def test_submission_isolation(self):
        # ایجاد یک پاسخ برای کاربر اول
        Submission.objects.create(
            user=self.user1,
            exercise=self.exercise,
            submitted_code="print('Hello from user1')"
        )
        
        # لاگین با کاربر دوم و چک کردن لیست پاسخ‌ها
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(self.submissions_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # کاربر دوم نباید پاسخ‌های کاربر اول را ببیند
        self.assertEqual(len(response.data), 0)