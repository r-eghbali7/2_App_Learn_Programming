# articles/tests.py
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .models import Article

class ArticleAPITests(APITestCase):
    def setUp(self):
        # ساخت یک مقاله فعال
        self.active_article = Article.objects.create(
            title="مقاله اول - فلاتر",
            summary="خلاصه مقاله اول",
            content="متن کامل آموزش فلاتر",
            is_active=True
        )
        
        # ساخت یک مقاله غیرفعال (پیش‌نویس)
        self.inactive_article = Article.objects.create(
            title="مقاله غیرفعال",
            summary="خلاصه مقاله دوم",
            content="این مقاله نباید در خروجی API نمایش داده شود",
            is_active=False
        )
        
        self.list_url = reverse('article-list')
        self.detail_url = reverse('article-detail', args=[self.active_article.id])

    def test_get_article_list(self):
        # درخواست لیست مقالات (بدون نیاز به لاگین)
        response = self.client.get(self.list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # فقط باید مقاله فعال برگردد
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['title'], "مقاله اول - فلاتر")
        
        # بررسی اینکه در لیست، فیلد متن کامل (content) وجود نداشته باشد (سبک بودن API)
        self.assertIn('summary', response.data[0])
        self.assertNotIn('content', response.data[0])

    def test_get_article_detail(self):
        # درخواست جزئیات مقاله
        response = self.client.get(self.detail_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], "مقاله اول - فلاتر")
        # در جزئیات، فیلد متن کامل باید وجود داشته باشد
        self.assertIn('content', response.data)