# courses/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from .models import Course, Lesson, UserProgress, UserNote
from .serializers import CourseListSerializer, CourseDetailSerializer, UserNoteSerializer

class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    """
    نمایش لیست دوره‌ها و جزئیات آن‌ها
    """
    queryset = Course.objects.filter(is_active=True).prefetch_related('lessons')
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.action == 'list':
            return CourseListSerializer
        return CourseDetailSerializer


class LessonActionViewSet(viewsets.ViewSet):
    """
    عملیات‌های مربوط به هر جلسه شامل: ذخیره یادداشت و تیک زدن تکمیل جلسه (دکمه آموزش بعدی)
    """
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'], url_path='toggle-complete')
    def toggle_complete(self, request, pk=None):
        try:
            lesson = Lesson.objects.get(pk=pk)
            progress, created = UserProgress.objects.get_or_create(user=request.user, lesson=lesson)
            if not created:
                # اگر از قبل بود، وضعیتش را برعکس کن (مثلا کاربر تیک را برمی‌دارد)
                progress.is_completed = not progress.is_completed
                progress.save()
            return Response({'status': 'success', 'is_completed': progress.is_completed})
        except Lesson.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post', 'get'], url_path='note')
    def manage_note(self, request, pk=None):
        try:
            lesson = Lesson.objects.get(pk=pk)
        except Lesson.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        if request.method == 'GET':
            note = UserNote.objects.filter(user=request.user, lesson=lesson).first()
            if note:
                return Response(UserNoteSerializer(note).data)
            return Response({'text': ''})

        elif request.method == 'POST':
            text = request.data.get('text', '')
            note, created = UserNote.objects.update_or_create(
                user=request.user, lesson=lesson,
                defaults={'text': text}
            )
            return Response({'status': 'success', 'note': UserNoteSerializer(note).data})