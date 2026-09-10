# subscriptions/views.py
import requests
from datetime import timedelta
from django.conf import settings
from django.shortcuts import redirect
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import ListAPIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Plan, Transaction, UserSubscription
from .serializers import (
    PlanSerializer,
    TransactionSerializer,
    UserSubscriptionSerializer,
)

class PlanViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Plan.objects.filter(is_active=True)
    serializer_class = PlanSerializer
    permission_classes = [AllowAny]


class MySubscriptionViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['get'])
    def status(self, request):
        sub = UserSubscription.objects.filter(
            user=request.user, 
            is_active=True,
            end_date__gt=timezone.now()
        ).order_by('-end_date').first()
        
        if sub and sub.is_valid:
            return Response(UserSubscriptionSerializer(sub).data)
        return Response({'message': 'شما اشتراک فعالی ندارید.', 'is_valid': False})


class PaymentRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        plan_id = request.data.get('plan_id')
        if not plan_id:
            return Response({"error": "شناسه پلن ارسال نشده است."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            plan = Plan.objects.get(id=plan_id, is_active=True)
        except Plan.DoesNotExist:
            return Response({"error": "پلن مورد نظر یافت نشد."}, status=status.HTTP_404_NOT_FOUND)

        amount_in_rials = int(plan.price) * 10
        merchant_id = getattr(settings, 'ZARINPAL_MERCHANT_ID', '00000000-0000-0000-0000-000000000000')

        payload = {
            "merchant_id": merchant_id,
            "amount": amount_in_rials,
            "callback_url": "http://127.0.0.1:8000/api/subscriptions/verify-payment/",
            "description": f"خرید اشتراک {plan.title} - کاربر {request.user.phone_number}",
            "metadata": {
                "mobile": str(request.user.phone_number),
            }
        }

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        try:
            response = requests.post(
                'https://payment.zarinpal.com/pg/v4/payment/request.json',
                json=payload,
                headers=headers,
                timeout=12
            )
            res_data = response.json()
            data = res_data.get('data', {})
            code = data.get('code')

            if code == 100:
                authority = data.get('authority')
                
                # رفع باگ حیاتی: ذخیره رکورد تراکنش در وضعیت در حال انتظار
                Transaction.objects.create(
                    user=request.user,
                    plan=plan,
                    amount=plan.price,
                    authority=authority,
                    status='pending'
                )

                payment_url = f"https://payment.zarinpal.com/pg/StartPay/{authority}"
                return Response({"payment_url": payment_url}, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"error": "خطا در اتصال به درگاه زرین‌پال", "details": res_data}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

        except Exception as e:
            return Response({"error": f"خطای ارتباط با درگاه: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PaymentVerifyView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        authority = request.GET.get('Authority')
        status_val = request.GET.get('Status')

        if not authority:
            return redirect("codeglass://payment-success?status=NOK&reason=missing_authority")

        try:
            transaction = Transaction.objects.get(authority=authority)
        except Transaction.DoesNotExist:
            return redirect("codeglass://payment-success?status=NOK&reason=transaction_not_found")

        if status_val != 'OK':
            transaction.status = 'failed'
            transaction.save()
            return redirect("codeglass://payment-success?status=NOK")

        merchant_id = getattr(settings, 'ZARINPAL_MERCHANT_ID', '00000000-0000-0000-0000-000000000000')
        payload = {
            "merchant_id": merchant_id,
            "amount": int(transaction.amount) * 10,
            "authority": authority
        }

        try:
            response = requests.post(
                'https://payment.zarinpal.com/pg/v4/payment/verify.json',
                json=payload,
                headers={'Content-Type': 'application/json'},
                timeout=12
            )
            res_data = response.json()
            data = res_data.get('data', {})
            code = data.get('code')

            if code in [100, 101]:
                ref_id = str(data.get('ref_id', ''))
                transaction.status = 'success'
                transaction.ref_id = ref_id
                transaction.save()

                # رفع باگ: فعال‌سازی صحیح اشتراک برای کاربر
                user = transaction.user
                plan = transaction.plan

                if plan:
                    now = timezone.now()
                    # بررسی اینکه آیا کاربر از قبل اشتراک فعالی دارد یا خیر
                    current_sub = UserSubscription.objects.filter(
                        user=user, 
                        is_active=True, 
                        end_date__gt=now
                    ).order_by('-end_date').first()

                    start_date = current_sub.end_date if current_sub else now
                    end_date = start_date + timedelta(days=plan.duration_days)

                    UserSubscription.objects.create(
                        user=user,
                        plan=plan,
                        end_date=end_date,
                        is_active=True
                    )

                return redirect(f"codeglass://payment-success?ref_id={ref_id}")
            else:
                transaction.status = 'failed'
                transaction.save()
                return redirect("codeglass://payment-success?status=NOK")

        except Exception:
            transaction.status = 'failed'
            transaction.save()
            return redirect("codeglass://payment-success?status=NOK&reason=server_error")


class UserPurchasesView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TransactionSerializer

    def get_queryset(self):
        return Transaction.objects.filter(user=self.request.user).order_by('-created_at')