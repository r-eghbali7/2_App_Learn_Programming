# courses/services.py
import os
from io import BytesIO
from django.conf import settings
from django.core.files.base import ContentFile
from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display

def write_persian_text(draw, text, position, font, text_color=(0, 0, 0)):
    """تابع کمکی برای نوشتن متن فارسی بدون به هم ریختگی"""
    reshaped_text = arabic_reshaper.reshape(text)
    bidi_text = get_display(reshaped_text)
    # از آنجایی که Pillow نقطه لنگر (Anchor) متفاوتی دارد، راست‌چین کردن دقیق نیاز به محاسبه عرض دارد
    # اما برای سادگی، شما باید x, y را در فتوشاپ برای این قالب پیدا کرده و اینجا جایگذاری کنید
    draw.text(position, bidi_text, font=font, fill=text_color, anchor="rm") # rm = Right Middle

def generate_certificate_image(certificate_obj, user_name, course_name, issue_date):
    # مسیر عکس خام و فونت
    template_path = os.path.join(settings.MEDIA_ROOT, 'certificates', 'template.jpg')
    font_path = os.path.join(settings.MEDIA_ROOT, 'fonts', 'Vazirmatn-Bold.ttf')
    
    # باز کردن عکس خام
    image = Image.open(template_path)
    draw = ImageDraw.Draw(image)
    
    # تنظیم سایز فونت‌ها
    font_large = ImageFont.truetype(font_path, 60)
    font_medium = ImageFont.truetype(font_path, 40)
    
    # === مختصات (X, Y) را باید بر اساس ابعاد عکستان تنظیم کنید ===
    # به عنوان مثال (اعداد حدودی هستند):
    write_persian_text(draw, user_name, position=(1400, 650), font=font_large)
    write_persian_text(draw, course_name, position=(1400, 850), font=font_large)
    write_persian_text(draw, issue_date, position=(1000, 1150), font=font_medium)
    write_persian_text(draw, certificate_obj.cert_id, position=(1000, 1250), font=font_medium)
    
    # ذخیره عکس در حافظه موقت و سپس در دیتابیس
    img_io = BytesIO()
    image.save(img_io, format='JPEG', quality=90)
    img_content = ContentFile(img_io.getvalue(), name=f"{certificate_obj.cert_id}.jpg")
    
    certificate_obj.image.save(f"{certificate_obj.cert_id}.jpg", img_content, save=True)