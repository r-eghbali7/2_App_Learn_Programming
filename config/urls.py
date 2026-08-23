from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/accounts/', include('accounts.urls')),
    path('api/courses/', include('courses.urls')), 
    path('api/articles/', include('articles.urls')),
    path('api/tickets/', include('tickets.urls')),
    path('api/subscriptions/', include('subscriptions.urls')),
    path('api/practices/', include('practices.urls')),
]