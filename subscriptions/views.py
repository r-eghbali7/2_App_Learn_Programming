from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from .models import Plan, UserSubscription
from .serializers import PlanSerializer, UserSubscriptionSerializer
from django.utils import timezone

class PlanViewSet(viewsets.ReadOnlyModelViewSet):
    """نمایش لیست پلن‌های اشتراک (برای صفحه خرید)"""
    queryset = Plan.objects.filter(is_active=True)
    serializer_class = PlanSerializer
    permission_classes = [AllowAny]

class MySubscriptionViewSet(viewsets.ViewSet):
    """بررسی وضعیت اشتراک کاربر و شبیه‌سازی خرید"""
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def status(self, request):
        # دریافت آخرین اشتراک کاربر
        sub = UserSubscription.objects.filter(user=request.user).order_by('-end_date').first()
        if sub and sub.is_valid:
            return Response(UserSubscriptionSerializer(sub).data)
        return Response({'message': 'شما اشتراک فعالی ندارید.', 'is_valid': False})

    @action(detail=False, methods=['post'])
    def mock_buy(self, request):
        """یک اندپوینت موقت برای تست فرآیند اختصاص پلن به کاربر"""
        plan_id = request.data.get('plan_id')
        try:
            plan = Plan.objects.get(id=plan_id, is_active=True)
            # غیرفعال کردن اشتراک‌های قبلی
            UserSubscription.objects.filter(user=request.user, is_active=True).update(is_active=False)
            
            sub = UserSubscription.objects.create(user=request.user, plan=plan)
            return Response(UserSubscriptionSerializer(sub).data, status=status.HTTP_201_CREATED)
        except Plan.DoesNotExist:
            return Response({'error': 'پلن یافت نشد.'}, status=status.HTTP_404_NOT_FOUND)