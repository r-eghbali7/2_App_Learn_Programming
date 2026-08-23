# accounts/services.py
from kavenegar import *
from django.conf import settings
import random

def generate_otp_code():
    return str(random.randint(10000, 99999)) # کد 5 رقمی

def send_otp_sms(phone_number, code):
    try:
        api = KavenegarAPI('6D4B7557415A7974556D37755977535830755A72476250327035484E674147634C586F376F544B56684E343D')  # جایگزین کردن با کلید API خود
        params = {
            'receptor': phone_number,
            'template': 'goldestone', # نام قالبی که در پنل کاوه نگار تایید کرده‌اید
            'token': code,
            'type': 'sms'# optional
        }
        response = api.verify_lookup(params)
        return True
    except APIException as e: 
        print(f"Kavenegar API Error: {e}")
        return False
    except HTTPException as e: 
        print(f"Kavenegar HTTP Error: {e}")
        return False