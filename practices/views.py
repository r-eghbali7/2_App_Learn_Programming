from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Exercise, Submission
from .serializers import ExerciseSerializer, SubmissionSerializer

class ExerciseViewSet(viewsets.ReadOnlyModelViewSet):
    """نمایش لیست تمرین‌ها"""
    queryset = Exercise.objects.filter(is_active=True)
    serializer_class = ExerciseSerializer
    permission_classes = [IsAuthenticated]

class SubmissionViewSet(viewsets.ModelViewSet):
    """ارسال پاسخ تمرین و مشاهده لیست پاسخ‌های قبلی کاربر"""
    serializer_class = SubmissionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Submission.objects.filter(user=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)