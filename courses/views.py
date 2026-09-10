# courses/views.py
from django.db.models import Prefetch
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.filters import SearchFilter

from core.utils import convert_to_shamsi
from .services import generate_certificate_image
from .models import Certificate, Course, Chapter, Lesson, UserProgress, UserNote, CourseEnrollment
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
    search_fields = ['title', 'instructor_name', 'description']

    def get_queryset(self):
        user = self.request.user
        queryset = Course.objects.filter(is_active=True)

        if self.action == 'retrieve' and user.is_authenticated:
            chapters_prefetch = Prefetch(
                'chapters',
                queryset=Chapter.objects.prefetch_related(
                    Prefetch(
                        'lessons',
                        queryset=Lesson.objects.prefetch_related(
                            Prefetch('completed_by', queryset=UserProgress.objects.filter(user=user, is_completed=True), to_attr='user_progress'),
                            Prefetch('notes', queryset=UserNote.objects.filter(user=user), to_attr='user_notes')
                        )
                    )
                )
            )
            return queryset.prefetch_related(chapters_prefetch)
        
        return queryset.prefetch_related('chapters__lessons')

    @action(detail=False, methods=['get'], url_path='my-courses', permission_classes=[IsAuthenticated])
    def my_courses(self, request):
        """لیست دوره‌هایی که کاربر ثبت‌نام کرده یا پیشرفتی در آن‌ها داشته است"""
        user = request.user
        # دوره‌هایی که خریده یا حداقل یک جلسه از آن را گذرانده
        enrolled_course_ids = CourseEnrollment.objects.filter(user=user).values_list('course_id', flat=True)
        in_progress_course_ids = UserProgress.objects.filter(user=user).values_list('lesson__chapter__course_id', flat=True)
        
        all_ids = set(list(enrolled_course_ids) + list(in_progress_course_ids))
        courses = Course.objects.filter(id__in=all_ids, is_active=True)
        
        serializer = MyCourseSerializer(courses, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get'], url_path='certificate', permission_classes=[IsAuthenticated])
    def get_certificate(self, request, pk=None):
        user = request.user
        course = self.get_object()

        total_lessons = Lesson.objects.filter(chapter__course=course).count()
        if total_lessons == 0:
            return Response({'error': 'این دوره جلسه‌ای ندارد.'}, status=status.HTTP_400_BAD_REQUEST)
            
        completed = UserProgress.objects.filter(user=user, lesson__chapter__course=course, is_completed=True).count()
        if completed < total_lessons:
            return Response({'error': 'برای صدور گواهینامه باید دوره را ۱۰۰٪ تکمیل کنید.'}, status=status.HTTP_403_FORBIDDEN)

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
            progress, created = UserProgress.objects.get_or_create(user=request.user, lesson=lesson, defaults={'is_completed': True})
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
            return Response(UserNoteSerializer(note).data if note else {'text': ''})

        elif request.method == 'POST':
            text = request.data.get('text', '')
            note, _ = UserNote.objects.update_or_create(user=request.user, lesson=lesson, defaults={'text': text})
            return Response({'status': 'success', 'note': UserNoteSerializer(note).data})