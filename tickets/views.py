from rest_framework import viewsets, parsers
from rest_framework.permissions import IsAuthenticated
from .models import Ticket
from .serializers import TicketSerializer

class TicketViewSet(viewsets.ModelViewSet):
    """
    کاربر می‌تواند لیست تیکت‌های خودش را ببیند، تیکت جدید بسازد و یک تیکت را با جزئیات بخواند.
    """
    serializer_class = TicketSerializer
    permission_classes = [IsAuthenticated]
    # اضافه کردن پارسرها برای پشتیبانی از آپلود فایل در API
    parser_classes = [parsers.MultiPartParser, parsers.FormParser, parsers.JSONParser]

    def get_queryset(self):
        # امنیت: هر کاربر فقط تیکت‌های خودش را می‌بیند
        return Ticket.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        # ثبت اتوماتیک کاربری که درخواست را ارسال کرده به عنوان صاحب تیکت
        serializer.save(user=self.request.user)