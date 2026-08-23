from rest_framework import serializers
from .models import Ticket

class TicketSerializer(serializers.ModelSerializer):
    # این فیلدها معادل فارسی وضعیت و موضوع را برای نمایش در UI فلاتر برمی‌گردانند
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    subject_display = serializers.CharField(source='get_subject_display', read_only=True)

    class Meta:
        model = Ticket
        fields = ['id', 'subject', 'subject_display', 'message', 'attachment', 'status', 'status_display', 'created_at']
        read_only_fields = ['status'] # کاربر نمی‌تواند وضعیت را موقع ارسال تغییر دهد