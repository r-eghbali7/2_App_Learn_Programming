# core/serializers.py
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
    # === فیلد جدید برای ارسال روزهای باقیمانده اشتراک ===
    subscription_remaining_days = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'phone_number', 'full_name', 'created_at', 'subscription_remaining_days']
        read_only_fields = ['phone_number', 'created_at']

    def get_created_at(self, obj):
        return convert_to_shamsi(obj.created_at, include_time=True)

    # === محاسبه روزهای باقیمانده ===
    def get_subscription_remaining_days(self, obj):
        from subscriptions.models import UserSubscription
        from django.utils import timezone
        
        # پیدا کردن آخرین اشتراک فعال کاربر که هنوز منقضی نشده است
        sub = UserSubscription.objects.filter(
            user=obj, 
            is_active=True, 
            end_date__gt=timezone.now()
        ).order_by('-end_date').first()
        
        if sub:
            delta = sub.end_date - timezone.now()
            return delta.days
        return 0

class UserProfileSerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField()
    subscription_remaining_days = serializers.SerializerMethodField()
    is_pro = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'phone_number', 'full_name', 'created_at', 'subscription_remaining_days', 'is_pro']
        read_only_fields = ['phone_number', 'created_at']

    def get_created_at(self, obj):
        return convert_to_shamsi(obj.created_at, include_time=True)

    def get_subscription_remaining_days(self, obj):
        from subscriptions.models import UserSubscription
        from django.utils import timezone
        sub = UserSubscription.objects.filter(user=obj, is_active=True, end_date__gt=timezone.now()).order_by('-end_date').first()
        return (sub.end_date - timezone.now()).days if sub else 0

    def get_is_pro(self, obj):
        return self.get_subscription_remaining_days(obj) > 0