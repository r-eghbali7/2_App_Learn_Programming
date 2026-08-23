from django.urls import path
from .views import HomeDashboardView, UserProfileView

urlpatterns = [
    path('home/', HomeDashboardView.as_view(), name='home-dashboard'),
    path('profile/', UserProfileView.as_view(), name='user-profile'),
]