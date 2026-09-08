# practices/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ExerciseViewSet, SubmissionViewSet

router = DefaultRouter()
router.register('exercises', ExerciseViewSet, basename='exercise')
router.register('submissions', SubmissionViewSet, basename='submission')

urlpatterns = [
    path('', include(router.urls)),
]