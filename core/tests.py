from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from .models import Banner
from courses.models import Course
from articles.models import Article

User = get_user_model()

class CoreAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(phone_number="09129999999", full_name="کاربر تستی")
        
        Banner.objects.create(title="تخفیف بهاره", is_active=True)
        Course.objects.create(title="دوره تستی فلاتر", description="توضیحات", instructor="مدرس", is_active=True)
        Article.objects.create(title="مقاله تستی", summary="خلاصه", content="متن", is_active=True)

        self.home_url = reverse('home-dashboard')
        self.profile_url = reverse('user-profile')

    def test_home_dashboard_aggregation(self):
        response = self.client.get(self.home_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # بررسی وجود هر ۳ بخش در خروجی
        self.assertIn('banners', response.data)
        self.assertIn('latest_courses', response.data)
        self.assertIn('latest_articles', response.data)
        
        self.assertEqual(len(response.data['banners']), 1)
        self.assertEqual(len(response.data['latest_courses']), 1)

    def test_get_user_profile(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.profile_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['full_name'], "کاربر تستی")
        self.assertEqual(response.data['phone_number'], "09129999999")

    def test_update_user_profile(self):
        self.client.force_authenticate(user=self.user)
        data = {'full_name': "اسم جدید من"}
        response = self.client.put(self.profile_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.full_name, "اسم جدید من")