import requests

from django.shortcuts import redirect

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



class PaymentRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            print("DATA RECEIVED:", request.data)
            plan_id = request.data.get('plan_id')
            
            if not plan_id:
                return Response({"error": "شناسه پلن ارسال نشده است."}, status=status.HTTP_400_BAD_REQUEST)

            try:
                plan = Plan.objects.get(id=plan_id)
            except Plan.DoesNotExist:
                print(f"Plan with id {plan_id} does not exist.")
                return Response({"error": "پلن مورد نظر یافت نشد."}, status=status.HTTP_400_BAD_REQUEST)

            # مبلغ به ریال
            amount_in_rials = int(plan.price) * 10 

            payload = {
                "merchant_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
                "amount": amount_in_rials,
                "callback_url": "http://127.0.0.1:8000/api/subscriptions/verify-payment/",
                "description": f"خرید اشتراک {plan.title}",
                "metadata": {
                    "mobile": str(request.user.phone_number),
                }
            }

            headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }

            response = requests.post(
                'https://payment.zarinpal.com/pg/v4/payment/request.json',
                json=payload,
                headers=headers,
                timeout=10
            )
            res_data = response.json()
            print("ZARINPAL RESPONSE:", res_data)

            data = res_data.get('data', {})
            code = data.get('code')

            if code == 100:
                authority = data.get('authority')
                payment_url = f"https://payment.zarinpal.com/pg/StartPay/{authority}"
                return Response({"payment_url": payment_url}, status=status.HTTP_200_OK)
            else:
                return Response({"error": "خطا از سمت درگاه زرین‌پال", "details": res_data}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print("CRITICAL PAYMENT ERROR:", str(e))
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# subscriptions/views.py (ادامه)
from django.shortcuts import redirect

class PaymentVerifyView(APIView):
    permission_classes = [] # چون از درگاه برمی‌گردد معمولا دسترسی عمومی دارد اما با authority چک می‌شود

    def get(self, request):
        authority = request.GET.get('Authority')
        status_val = request.GET.get('Status')

        try:
            transaction = Transaction.objects.get(authority=authority)
        except Transaction.DoesNotExist:
            return Response({"error": "تراکنش یافت نشد."}, status=status.HTTP_404_NOT_FOUND)

        if status_val != 'OK':
            transaction.status = 'failed'
            transaction.save()
            # ریدایرکت به اپلیکیشن فلاتر با دیپ‌لینک خطا
            return redirect("codeglass://payment-success?status=NOK")

        # اطلاعات برای متد Verify بر اساس مستندات v4
        payload = {
            "merchant_id": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
            "amount": int(transaction.amount) * 10,
            "authority": authority
        }

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

        response = requests.post(
            'https://payment.zarinpal.com/pg/v4/payment/verify.json',
            json=payload,
            headers=headers
        )
        res_data = response.json()
        data = res_data.get('data', {})
        code = data.get('code')

        # کد 100 یا 101 به معنی موفق بودن تراکنش است (طبق مستندات مهم زرین‌پال)
        if code in [100, 101]:
            ref_id = data.get('ref_id')
            
            transaction.status = 'success'
            transaction.ref_id = str(ref_id)
            transaction.save()

            # فعال کردن اشتراک برای کاربر
            user = transaction.user
            user.is_pro = True
            user.save()

            # ریدایرکت به دیپ‌لینک فلاتر همراه با کد پیگیری (Ref ID)
            return redirect(f"codeglass://payment-success?ref_id={ref_id}")
        else:
            transaction.status = 'failed'
            transaction.save()
            return redirect("codeglass://payment-success?status=NOK")



class UserPurchasesView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = TransactionSerializer

    def get_queryset(self):
        # فقط خریدهای همین کاربر لاگین‌شده را برمی‌گرداند
        return Transaction.objects.filter(user=self.request.user).order_by('-created_at')