from rest_framework import serializers
from .models import Plan, Transaction, UserSubscription

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


class TransactionSerializer(serializers.ModelSerializer):
    plan_title = serializers.CharField(source='plan.title', read_only=True)

    class Meta:
        model = Transaction
        fields = ['id', 'plan_title', 'amount', 'ref_id', 'status', 'created_at']