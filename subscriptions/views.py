import requests
import json
from django.conf import settings
from django.urls import reverse
from django.http import HttpResponseRedirect, HttpResponse
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.views import APIView

from .models import Plan, UserSubscription, Transaction
from .serializers import PlanSerializer, UserSubscriptionSerializer

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
    """
    مرحله اول: ایجاد تراکنش و دریافت لینک درگاه پرداخت
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        plan_id = request.data.get('plan_id')
        try:
            plan = Plan.objects.get(id=plan_id, is_active=True)
        except Plan.DoesNotExist:
            return Response({'error': 'پلن یافت نشد.'}, status=status.HTTP_404_NOT_FOUND)

        amount_toman = plan.price
        amount_rial = amount_toman * 10  # زرین‌پال مبالغ را به ریال دریافت می‌کند

        # آدرس کال‌بک (بازگشت از درگاه)
        # در سرور واقعی، دامنه سایت خودتان را جایگزین 127.0.0.1 کنید
        callback_url = "http://127.0.0.1:8000" + reverse('verify-payment')

        data = {
            "merchant_id": settings.ZARINPAL_MERCHANT_ID,
            "amount": amount_rial,
            "callback_url": callback_url,
            "description": f"خرید اشتراک {plan.title} برای {request.user.phone_number}",
            "metadata": {"mobile": request.user.phone_number}
        }
        
        headers = {'content-type': 'application/json', 'accept': 'application/json'}
        
        try:
            req = requests.post('https://api.zarinpal.com/pg/v4/payment/request.json', data=json.dumps(data), headers=headers)
            res = req.json()
            
            if len(res['errors']) == 0:
                authority = res['data']['authority']
                
                # ثبت تراکنش در دیتابیس در حالت پرداخت نشده (Pending)
                Transaction.objects.create(
                    user=request.user,
                    plan=plan,
                    amount=amount_toman,
                    authority=authority
                )
                
                payment_url = f"https://www.zarinpal.com/pg/StartPay/{authority}"
                return Response({'payment_url': payment_url}, status=status.HTTP_200_OK)
            else:
                return Response({'error': res['errors']}, status=status.HTTP_400_BAD_REQUEST)
                
        except requests.exceptions.Timeout:
            return Response({'error': 'Timeout'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except requests.exceptions.ConnectionError:
            return Response({'error': 'Connection Error'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class PaymentVerifyView(APIView):
    """
    مرحله دوم: بازگشت کاربر از درگاه و بررسی وضعیت پرداخت
    """
    permission_classes = [AllowAny] # چون کاربر از سمت زرین‌پال برمی‌گردد، هدر احراز هویت ندارد

    def get(self, request):
        authority = request.GET.get('Authority')
        payment_status = request.GET.get('Status')

        if payment_status != 'OK':
            return HttpResponse("<b>پرداخت ناموفق بود یا توسط شما لغو شد.</b><br><a href='codeglass://app'>بازگشت به اپلیکیشن</a>")

        try:
            transaction = Transaction.objects.get(authority=authority, is_paid=False)
        except Transaction.DoesNotExist:
            return HttpResponse("<b>تراکنش یافت نشد یا قبلاً تایید شده است.</b>")

        amount_rial = transaction.amount * 10
        data = {
            "merchant_id": settings.ZARINPAL_MERCHANT_ID,
            "amount": amount_rial,
            "authority": authority
        }
        headers = {'content-type': 'application/json', 'accept': 'application/json'}

        try:
            req = requests.post('https://api.zarinpal.com/pg/v4/payment/verify.json', data=json.dumps(data), headers=headers)
            res = req.json()

            if len(res['errors']) == 0:
                code = res['data']['code']
                if code == 100 or code == 101: # 100: موفق، 101: قبلا وریفای شده
                    # ۱. تراکنش را موفق ثبت می‌کنیم
                    transaction.is_paid = True
                    transaction.ref_id = str(res['data']['ref_id'])
                    transaction.save()

                    # ۲. غیرفعال کردن اشتراک‌های قبلی کاربر
                    UserSubscription.objects.filter(user=transaction.user, is_active=True).update(is_active=False)
                    
                    # ۳. فعال کردن اشتراک جدید
                    UserSubscription.objects.create(user=transaction.user, plan=transaction.plan)

                    # هدایت کاربر به اپلیکیشن از طریق Deep Link
                    # کلمه codeglass:// باید در تنظیمات AndroidManifest فلاتر ست شود
                    return HttpResponseRedirect(f"codeglass://payment-success?ref_id={transaction.ref_id}")
                else:
                    return HttpResponse(f"<b>تراکنش ناموفق بود. کد خطا: {code}</b>")
            else:
                return HttpResponse(f"<b>تراکنش ناموفق بود. خطا: {res['errors']}</b>")

        except Exception as e:
            return HttpResponse("<b>خطا در ارتباط با سرور زرین‌پال.</b>")