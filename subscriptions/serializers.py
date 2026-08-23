from rest_framework import serializers
from .models import Plan, UserSubscription

class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = ['id', 'title', 'duration_days', 'price', 'description']

class UserSubscriptionSerializer(serializers.ModelSerializer):
    plan_title = serializers.CharField(source='plan.title', read_only=True)
    is_valid = serializers.BooleanField(read_only=True)

    class Meta:
        model = UserSubscription
        fields = ['id', 'plan_title', 'start_date', 'end_date', 'is_valid']