from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ExerciseViewSet, SubmissionViewSet

router = DefaultRouter()
router.register(r'exercises', ExerciseViewSet, basename='exercise')
router.register(r'submissions', SubmissionViewSet, basename='submission')

urlpatterns = [
    path('', include(router.urls)),
]