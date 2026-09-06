from rest_framework import serializers
from .models import Ticket
from core.utils import convert_to_shamsi

class TicketSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    subject_display = serializers.CharField(source='get_subject_display', read_only=True)
    created_at = serializers.SerializerMethodField()

    class Meta:
        model = Ticket
        fields = ['id', 'subject', 'subject_display', 'message', 'attachment', 'status', 'status_display', 'created_at']
        read_only_fields = ['status']

    def get_created_at(self, obj):
        # برای تیکت معمولاً دیدن ساعت ارسال هم مهم است
        return convert_to_shamsi(obj.created_at, include_time=True)