# courses/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CourseViewSet, LessonActionViewSet

router = DefaultRouter()
router.register(r'list', CourseViewSet, basename='course')
router.register(r'lesson', LessonActionViewSet, basename='lesson-action')

urlpatterns = [
    path('', include(router.urls)),
]