# tickets/tests.py
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from .models import Ticket

User = get_user_model()

class TicketAPITests(APITestCase):
    def setUp(self):
        # ساخت دو کاربر مختلف برای تست ایزوله بودن تیکت‌ها
        self.user1 = User.objects.create_user(phone_number="09121111111", password="testpass1")
        self.user2 = User.objects.create_user(phone_number="09122222222", password="testpass2")
        
        # ساخت یک تیکت برای کاربر اول
        self.ticket1 = Ticket.objects.create(
            user=self.user1,
            subject="technical",
            message="اپلیکیشن روی گوشی من نصب نمی‌شود"
        )
        
        self.list_url = reverse('ticket-list')

    def test_unauthenticated_access(self):
        # کاربری که لاگین نکرده نباید دسترسی داشته باشد
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_ticket_isolation(self):
        # لاگین با کاربر اول
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1) # تیکت خودش را می‌بیند
        self.assertEqual(response.data[0]['message'], "اپلیکیشن روی گوشی من نصب نمی‌شود")
        
        # تغییر کاربر به کاربر دوم
        self.client.force_authenticate(user=self.user2)
        response = self.client.get(self.list_url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0) # لیست تیکت‌هایش باید خالی باشد

    def test_create_ticket_without_attachment(self):
        self.client.force_authenticate(user=self.user1)
        data = {
            'subject': 'financial',
            'message': 'مشکل در درگاه پرداخت'
        }
        response = self.client.post(self.list_url, data)
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Ticket.objects.count(), 2)
        
        # بررسی اینکه تیکت جدید متعلق به کاربر اول است و وضعیتش pending است
        new_ticket = Ticket.objects.latest('created_at')
        self.assertEqual(new_ticket.user, self.user1)
        self.assertEqual(new_ticket.status, 'pending')

    def test_create_ticket_with_attachment(self):
        self.client.force_authenticate(user=self.user1)
        
        # شبیه‌سازی یک فایل موقت برای آپلود
        dummy_file = SimpleUploadedFile(
            "screenshot.jpg",
            b"file_content_goes_here",
            content_type="image/jpeg"
        )
        
        data = {
            'subject': 'educational',
            'message': 'منظور استاد در این بخش چیست؟ ضمیمه را ببینید.',
            'attachment': dummy_file
        }
        
        # format='multipart' برای شبیه‌سازی ارسال فایل از فرم در فرانت‌اند ضروری است
        response = self.client.post(self.list_url, data, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # بررسی می‌کنیم که نام فایل در دیتابیس ثبت شده باشد
        new_ticket = Ticket.objects.latest('created_at')
        self.assertTrue(new_ticket.attachment.name.startswith('tickets/attachments/'))