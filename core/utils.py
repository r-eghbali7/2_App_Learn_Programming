# core/utils.py
import jdatetime
from django.utils.timezone import localtime

def convert_to_shamsi(date_obj, include_time=False):
    if not date_obj:
        return ""
    
    local_time = localtime(date_obj)
    jalali_date = jdatetime.datetime.fromgregorian(datetime=local_time)
    
    if include_time:
        return jalali_date.strftime('%d %B %Y، %H:%M')
    else:
        return jalali_date.strftime('%d %B %Y')