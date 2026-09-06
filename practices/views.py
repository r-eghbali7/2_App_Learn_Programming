# practices/views.py
import requests
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Exercise, Submission
from .serializers import ExerciseSerializer, SubmissionSerializer

class ExerciseViewSet(viewsets.ReadOnlyModelViewSet):
    """نمایش لیست تمرین‌ها"""
    queryset = Exercise.objects.filter(is_active=True)
    serializer_class = ExerciseSerializer
    permission_classes = [IsAuthenticated]

class SubmissionViewSet(viewsets.ModelViewSet):
    """ارسال پاسخ تمرین و اجرای زنده کد توسط Piston API"""
    serializer_class = SubmissionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Submission.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        # 1. ذخیره اولیه کد در دیتابیس با وضعیت Pending
        submission = serializer.save(user=self.request.user, status='pending')
        exercise = submission.exercise

        # 2. مپ کردن زبان انتخابی در سیستم شما به نام‌های استاندارد Piston
        # Piston از نام دقیق زبان‌ها استفاده می‌کند.
        language_map = {
            'JS': 'javascript',
            'Python': 'python',
            'C++': 'cpp',
            'Java': 'java',
        }
        
        # اگر زبان در مپ ما نبود، همان نام را با حروف کوچک می‌فرستیم
        piston_lang = language_map.get(exercise.language, str(exercise.language).lower())

        # 3. ساخت Payload برای ارسال به Piston API
        payload = {
            "language": piston_lang,
            "version": "*", # آخرین نسخه زبان را استفاده می‌کند
            "files": [
                {
                    "content": submission.submitted_code
                }
            ],
            # در صورتی که تمرین نیاز به ورودی خاصی (stdin) دارد می‌توانید اینجا اضافه کنید
            "stdin": "", 
            "args": [],
            "compile_timeout": 10000, # میلی‌ثانیه
            "run_timeout": 3000,      # جلوگیری از حلقه‌های بی‌نهایت (While True)
            "compile_memory_limit": -1,
            "run_memory_limit": -1
        }

        # 4. ارسال درخواست به سرور عمومی Piston (EngineerMan)
        piston_url = "https://emacs.piston.rs/api/v2/execute"
        headers = {'Content-Type': 'application/json'}

        try:
            response = requests.post(piston_url, json=payload, headers=headers, timeout=15)
            
            if response.status_code == 200:
                result = response.json()
                
                # Piston دو بخش دارد: compile و run
                # اگر خطای کامپایل داشته باشیم:
                if 'compile' in result and result['compile']['code'] != 0:
                    submission.status = 'failed'
                    submission.feedback = f"خطای کامپایل:\n{result['compile']['stderr']}"
                
                # اگر کد کامپایل شد اما در زمان اجرا خطا داد:
                elif 'run' in result and result['run']['code'] != 0:
                    submission.status = 'failed'
                    submission.feedback = f"خطای زمان اجرا:\n{result['run']['stderr']}"
                
                # اگر کد با موفقیت اجرا شد:
                else:
                    output = result['run']['stdout']
                    
                    # 5. سیستم اعتبارسنجی (Validation):
                    # شما باید خروجی را با جواب مورد انتظار تمرین مقایسه کنید.
                    # برای مثال، اگر خروجی باید "Hello World" باشد:
                    # (در دنیای واقعی، جواب مورد انتظار را باید به مدل Exercise اضافه کنید)
                    # expected_output = exercise.expected_output
                    
                    # در اینجا فرض می‌کنیم اگر کد بدون خطا اجرا شد، پاس شده است.
                    # اگر می‌خواهید خروجی را به کاربر نشان دهید، آن را در فیدبک می‌گذاریم.
                    submission.status = 'passed'
                    submission.feedback = f"خروجی برنامه:\n{output}"
            else:
                submission.status = 'failed'
                submission.feedback = "خطا در ارتباط با سرور پردازش کد."

        except requests.exceptions.Timeout:
            submission.status = 'failed'
            submission.feedback = "زمان اجرای برنامه شما بیش از حد طول کشید (Timeout). احتمالاً حلقه بی‌نهایت دارید."
        except Exception as e:
            submission.status = 'failed'
            submission.feedback = "خطای غیرمنتظره در سرور ارزیابی."

        # ذخیره نهایی وضعیت اجرای کد در دیتابیس
        submission.save()