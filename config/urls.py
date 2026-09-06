from django.contrib import admin
from django.urls import path, include
from django.conf import settings             # اضافه شد
from django.conf.urls.static import static   # اضافه شد

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/accounts/', include('accounts.urls')),
    path('api/courses/', include('courses.urls')), 
    path('api/articles/', include('articles.urls')),
    path('api/tickets/', include('tickets.urls')),
    path('api/subscriptions/', include('subscriptions.urls')),
    path('api/practices/', include('practices.urls')),
    path('api/core/', include('core.urls')), # این مسیر در فایل شما جا افتاده بود، آن را اضافه کردم
]

# سرو کردن فایل‌های مدیا در حالت دیباگ
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)