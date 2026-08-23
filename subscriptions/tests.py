# subscriptions/tests.py
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from .models import Plan, UserSubscription

User = get_user_model()

class SubscriptionAPITests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(phone_number="09121234567", password="testpass")
        
        # ساخت پلن‌های تستی
        self.plan_1_month = Plan.objects.create(
            title="پلن یک ماهه", duration_days=30, price=100000
        )
        self.plan_6_months = Plan.objects.create(
            title="پلن شش ماهه", duration_days=180, price=500000
        )

        self.plans_url = reverse('plan-list')
        self.status_url = reverse('my-subscription-status')
        self.buy_url = reverse('my-subscription-mock-buy')

    def test_get_plans_list(self):
        # دیدن پلن‌ها نیازی به لاگین ندارد
        response = self.client.get(self.plans_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['title'], "پلن یک ماهه")

    def test_user_without_subscription(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.get(self.status_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['is_valid'])
        self.assertEqual(response.data['message'], 'شما اشتراک فعالی ندارید.')

    def test_mock_buy_and_check_status(self):
        self.client.force_authenticate(user=self.user)
        
        # ۱. خرید پلن
        data = {'plan_id': self.plan_1_month.id}
        buy_response = self.client.post(self.buy_url, data)
        self.assertEqual(buy_response.status_code, status.HTTP_201_CREATED)
        
        # بررسی اینکه آیا تاریخ انقضا به درستی ۳۰ روز بعد تنظیم شده است
        sub = UserSubscription.objects.get(user=self.user)
        expected_end_date = sub.start_date + timedelta(days=30)
        # اختلاف در حد چند میلی‌ثانیه طبیعی است، پس تاریخ‌ها را مقایسه می‌کنیم
        self.assertAlmostEqual(sub.end_date.date(), expected_end_date.date())

        # ۲. بررسی وضعیت اشتراک بعد از خرید
        status_response = self.client.get(self.status_url)
        self.assertEqual(status_response.status_code, status.HTTP_200_OK)
        self.assertTrue(status_response.data['is_valid'])
        self.assertEqual(status_response.data['plan_title'], "پلن یک ماهه")

    def test_buy_new_plan_overrides_old_one(self):
        self.client.force_authenticate(user=self.user)
        
        # خرید اول (یک ماهه)
        self.client.post(self.buy_url, {'plan_id': self.plan_1_month.id})
        
        # خرید دوم (شش ماهه) - باید اولی را غیرفعال کند
        self.client.post(self.buy_url, {'plan_id': self.plan_6_months.id})
        
        # بررسی در دیتابیس
        active_subs = UserSubscription.objects.filter(user=self.user, is_active=True)
        self.assertEqual(active_subs.count(), 1)
        self.assertEqual(active_subs.first().plan, self.plan_6_months)