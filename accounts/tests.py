# accounts/tests.py
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from unittest.mock import patch
from .models import OTP

User = get_user_model()

class AccountAPITests(APITestCase):
    def setUp(self):
        # اطلاعات پایه برای تست‌ها
        self.phone_number = "09123456789"
        self.password = "StrongPass123"
        self.user = User.objects.create_user(
            phone_number=self.phone_number,
            password=self.password,
            full_name="تست کاربر"
        )
        # آدرس‌های URL (بر اساس نام‌هایی که در urls.py تعریف کردیم)
        self.send_otp_url = reverse('send-otp')
        self.verify_otp_url = reverse('verify-otp')
        self.change_password_url = reverse('change-password')
        self.reset_password_url = reverse('reset-password')

    @patch('accounts.views.send_otp_sms') # جلوگیری از ارسال پیامک واقعی
    def test_send_otp(self, mock_send_sms):
        mock_send_sms.return_value = True # فرض می‌کنیم پیامک با موفقیت ارسال شده
        
        data = {'phone_number': '09998887766'}
        response = self.client.post(self.send_otp_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(OTP.objects.filter(phone_number='09998887766').exists())
        self.assertTrue(mock_send_sms.called)

    def test_verify_otp_login_success(self):
        # ایجاد یک کد OTP معتبر در دیتابیس برای کاربر فعلی
        OTP.objects.create(phone_number=self.phone_number, code="12345")
        
        data = {
            'phone_number': self.phone_number,
            'code': "12345"
        }
        response = self.client.post(self.verify_otp_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', response.data)
        self.assertFalse(response.data['is_new_user'])

    def test_verify_otp_register_success(self):
        new_phone = "09112223344"
        OTP.objects.create(phone_number=new_phone, code="54321")
        
        data = {
            'phone_number': new_phone,
            'code': "54321",
            'full_name': "کاربر جدید",
            'password': "newpassword123"
        }
        response = self.client.post(self.verify_otp_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_new_user'])
        self.assertTrue(User.objects.filter(phone_number=new_phone).exists())

    def test_change_password(self):
        # کاربر باید لاگین باشد
        self.client.force_authenticate(user=self.user)
        
        data = {
            'old_password': self.password,
            'new_password': "NewStrongPass999"
        }
        response = self.client.post(self.change_password_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # تست می‌کنیم که آیا رمز واقعاً تغییر کرده است
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("NewStrongPass999"))

    def test_reset_password(self):
        OTP.objects.create(phone_number=self.phone_number, code="99887")
        
        data = {
            'phone_number': self.phone_number,
            'code': "99887",
            'new_password': "ResetPass456"
        }
        response = self.client.post(self.reset_password_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("ResetPass456"))