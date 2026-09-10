# courses/views.py
from django.db.models import Prefetch
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.filters import SearchFilter

from core.utils import convert_to_shamsi  # اضافه شد
from .services import generate_certificate_image  # اضافه شد

from .models import Certificate, Course, Lesson, UserProgress, UserNote
from .serializers import (
    CertificateSerializer, 
    CourseListSerializer, 
    CourseDetailSerializer, 
    MyCourseSerializer, 
    UserNoteSerializer
)

class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = CourseListSerializer
    filter_backends = [SearchFilter]
    search_fields = ['title', 'instructor', 'description']

    def get_queryset(self):
        user = self.request.user
        queryset = Course.objects.filter(is_active=True)

        if self.action == 'retrieve' and user.is_authenticated:
            lessons_prefetch = Prefetch(
                'lessons',
                queryset=Lesson.objects.prefetch_related(
                    Prefetch(
                        'completed_by', 
                        queryset=UserProgress.objects.filter(user=user, is_completed=True), 
                        to_attr='user_progress'
                    ),
                    Prefetch(
                        'notes', 
                        queryset=UserNote.objects.filter(user=user), 
                        to_attr='user_notes'
                    )
                )
            )
            return queryset.prefetch_related(lessons_prefetch)
        
        return queryset.prefetch_related('lessons')

    @action(detail=True, methods=['get'], url_path='certificate', permission_classes=[IsAuthenticated])
    def get_certificate(self, request, pk=None):
        user = request.user
        course = self.get_object()

        total_lessons = course.lessons.count()
        if total_lessons == 0:
            return Response({'error': 'این دوره هنوز جلسه‌ای ندارد.'}, status=status.HTTP_400_BAD_REQUEST)
            
        completed = UserProgress.objects.filter(user=user, lesson__course=course, is_completed=True).count()
        
        if completed < total_lessons:
            return Response({'error': 'برای دریافت گواهینامه باید تمام جلسات دوره را به اتمام برسانید.'}, status=status.HTTP_403_FORBIDDEN)

        cert, created = Certificate.objects.get_or_create(user=user, course=course)
        
        if created or not cert.image:
            user_name = user.full_name if user.full_name else "کاربر گرامی"
            issue_date = convert_to_shamsi(cert.issued_at)
            generate_certificate_image(cert, user_name, course.title, issue_date)

        cert_url = request.build_absolute_uri(cert.image.url)
        return Response({
            'status': 'success',
            'certificate_id': cert.cert_id,
            'download_url': cert_url
        }, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='my-certificates', permission_classes=[IsAuthenticated])
    def my_certificates(self, request):
        certificates = Certificate.objects.filter(user=request.user).exclude(image='').order_by('-issued_at')
        serializer = CertificateSerializer(certificates, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get_serializer_class(self):
        if self.action == 'list':
            return CourseListSerializer
        return CourseDetailSerializer


class LessonActionViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    @action(detail=True, methods=['post'], url_path='toggle-complete')
    def toggle_complete(self, request, pk=None):
        try:
            lesson = Lesson.objects.get(pk=pk)
            progress, created = UserProgress.objects.get_or_create(
                user=request.user, 
                lesson=lesson,
                defaults={'is_completed': True}
            )
            if not created:
                progress.is_completed = not progress.is_completed
                progress.save()
            return Response({'status': 'success', 'is_completed': progress.is_completed})
        except Lesson.DoesNotExist:
            return Response({'error': 'جلسه یافت نشد.'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post', 'get'], url_path='note')
    def manage_note(self, request, pk=None):
        try:
            lesson = Lesson.objects.get(pk=pk)
        except Lesson.DoesNotExist:
            return Response({'error': 'جلسه یافت نشد.'}, status=status.HTTP_404_NOT_FOUND)

        if request.method == 'GET':
            note = UserNote.objects.filter(user=request.user, lesson=lesson).first()
            if note:
                return Response(UserNoteSerializer(note).data)
            return Response({'text': ''})

        elif request.method == 'POST':
            text = request.data.get('text', '')
            note, _ = UserNote.objects.update_or_create(
                user=request.user, 
                lesson=lesson,
                defaults={'text': text}
            )
            return Response({'status': 'success', 'note': UserNoteSerializer(note).data})