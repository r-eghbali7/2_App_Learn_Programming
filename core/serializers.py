from rest_framework import serializers
from .models import Banner
from django.contrib.auth import get_user_model
from core.utils import convert_to_shamsi

User = get_user_model()

class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = ['id', 'title', 'image', 'link']

class UserProfileSerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'phone_number', 'full_name', 'created_at']
        read_only_fields = ['phone_number', 'created_at']

    def get_created_at(self, obj):
        # اگر می‌خواهید زمان ثبت‌نام هم نمایش داده شود:
        return convert_to_shamsi(obj.created_at, include_time=True)