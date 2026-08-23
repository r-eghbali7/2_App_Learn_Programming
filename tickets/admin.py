from django.contrib import admin
from .models import Ticket

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ['user', 'subject', 'status', 'created_at']
    list_filter = ['status', 'subject']
    search_fields = ['user__phone_number', 'message']
    # برای اینکه ادمین بتواند وضعیت تیکت را مستقیماً از لیست تغییر دهد:
    list_editable = ['status']