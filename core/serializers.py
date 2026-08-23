from rest_framework import serializers
from .models import Banner
from django.contrib.auth import get_user_model

User = get_user_model()

class BannerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Banner
        fields = ['id', 'title', 'image', 'link']

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'phone_number', 'full_name', 'created_at']
        read_only_fields = ['phone_number', 'created_at'] # شماره موبایل قابل تغییر نیست