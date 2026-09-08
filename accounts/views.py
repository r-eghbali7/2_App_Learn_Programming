# accounts/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate # این خط را به بالای فایل اضافه کنید

from accounts.throttles import OTPRateThrottle
from .models import User, OTP
from .serializers import SendOTPSerializer, VerifyOTPSerializer,ResetPasswordSerializer,ChangePasswordSerializer
from .services import generate_otp_code, send_otp_sms
from rest_framework.permissions import AllowAny, IsAuthenticated


class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        phone_number = request.data.get('phone_number')
        password = request.data.get('password')
        full_name = request.data.get('full_name', '')

        if not phone_number or not password:
            return Response({'error': 'شماره موبایل و رمز عبور الزامی است.'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(phone_number=phone_number).exists():
            return Response({'error': 'کاربری با این شماره قبلا ثبت‌نام کرده است.'}, status=status.HTTP_400_BAD_REQUEST)

        # ساخت کاربر جدید
        user = User.objects.create_user(phone_number=phone_number, password=password, full_name=full_name)
        refresh = RefreshToken.for_user(user)

        return Response({
            'message': 'ثبت‌نام موفقیت‌آمیز بود.',
            'access': str(refresh.access_token),
            'refresh': str(refresh),
        }, status=status.HTTP_201_CREATED)


class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        phone_number = request.data.get('phone_number')
        password = request.data.get('password')

        if not phone_number or not password:
            return Response({'error': 'شماره موبایل و رمز عبور الزامی است.'}, status=status.HTTP_400_BAD_REQUEST)

        # روش جایگزین و بسیار مطمئن به جای استفاده از authenticate
        user = User.objects.filter(phone_number=phone_number).first()

        # بررسی وجود کاربر و همچنین بررسی هش رمز عبور
        if user and user.check_password(password):
            if not user.is_active:
                return Response({'error': 'حساب کاربری شما مسدود شده است.'}, status=status.HTTP_403_FORBIDDEN)
            
            # تولید توکن
            refresh = RefreshToken.for_user(user)
            return Response({
                'message': 'ورود موفقیت‌آمیز بود.',
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            }, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'شماره موبایل یا رمز عبور اشتباه است.'}, status=status.HTTP_401_UNAUTHORIZED)

class SendOTPView(APIView):
    throttle_classes = [OTPRateThrottle]
    def post(self, request):
        serializer = SendOTPSerializer(data=request.data)
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']
            
            code = generate_otp_code()
            OTP.objects.filter(phone_number=phone_number).delete()
            OTP.objects.create(phone_number=phone_number, code=code)

            sms_sent = send_otp_sms(phone_number, code)
            
            if sms_sent:
                return Response({'message': 'کد تایید ارسال شد.'}, status=status.HTTP_200_OK)
            return Response({'error': 'خطا در ارسال پیامک'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VerifyOTPView(APIView):
    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']
            code = serializer.validated_data['code']
            full_name = serializer.validated_data.get('full_name', '')
            password = serializer.validated_data.get('password', None)

            try:
                otp_record = OTP.objects.get(phone_number=phone_number, code=code)
            except OTP.DoesNotExist:
                return Response({'error': 'کد تایید نامعتبر است.'}, status=status.HTTP_400_BAD_REQUEST)

            if not otp_record.is_valid():
                return Response({'error': 'کد تایید منقضی شده است.'}, status=status.HTTP_400_BAD_REQUEST)

            # بررسی وجود کاربر یا ثبت‌نام کاربر جدید
            user, created = User.objects.get_or_create(phone_number=phone_number)
            
            if created:
                # اگر کاربر جدید است و اطلاعات اضافی فرستاده، ذخیره می‌کنیم
                if full_name:
                    user.full_name = full_name
                if password:
                    user.set_password(password)
                user.save()

            # حذف کد استفاده شده
            otp_record.delete()

            # تولید توکن JWT
            refresh = RefreshToken.for_user(user)

            return Response({
                'message': 'ورود موفقیت‌آمیز بود.',
                'is_new_user': created,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    
class ResetPasswordView(APIView):
    """
    برای کاربری که رمزش را فراموش کرده است.
    ابتدا باید از طریق SendOTPView کد را دریافت کرده باشد.
    """
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        if serializer.is_valid():
            phone_number = serializer.validated_data['phone_number']
            code = serializer.validated_data['code']
            new_password = serializer.validated_data['new_password']

            # بررسی صحت کد OTP
            try:
                otp_record = OTP.objects.get(phone_number=phone_number, code=code)
            except OTP.DoesNotExist:
                return Response({'error': 'کد تایید نامعتبر است.'}, status=status.HTTP_400_BAD_REQUEST)

            if not otp_record.is_valid():
                return Response({'error': 'کد تایید منقضی شده است.'}, status=status.HTTP_400_BAD_REQUEST)

            # پیدا کردن کاربر و تغییر رمز
            try:
                user = User.objects.get(phone_number=phone_number)
                user.set_password(new_password)
                user.save()
                
                # حذف کد OTP پس از استفاده موفق
                otp_record.delete()
                
                return Response({'message': 'رمز عبور با موفقیت تغییر کرد.'}, status=status.HTTP_200_OK)
            except User.DoesNotExist:
                return Response({'error': 'کاربری با این شماره موبایل یافت نشد.'}, status=status.HTTP_404_NOT_FOUND)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ChangePasswordView(APIView):
    """
    برای کاربری که لاگین است و می‌خواهد رمزش را تغییر دهد.
    نیاز به توکن احراز هویت دارد.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            old_password = serializer.validated_data['old_password']
            new_password = serializer.validated_data['new_password']

            # بررسی اینکه آیا کاربر اصلاً رمز عبور دارد یا نه (شاید فقط با OTP وارد شده باشد)
            if not user.has_usable_password():
                # اگر تا به حال رمزی نداشته، فقط رمز جدید را برایش ست می‌کنیم
                user.set_password(new_password)
                user.save()
                return Response({'message': 'رمز عبور با موفقیت تنظیم شد.'}, status=status.HTTP_200_OK)

            # بررسی صحت رمز قبلی
            if not user.check_password(old_password):
                return Response({'error': 'رمز عبور فعلی اشتباه است.'}, status=status.HTTP_400_BAD_REQUEST)

            # تنظیم رمز جدید
            user.set_password(new_password)
            user.save()
            return Response({'message': 'رمز عبور با موفقیت تغییر کرد.'}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)