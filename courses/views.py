# courses/views.py
from django.db.models import Prefetch
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from .models import Course, Lesson, UserProgress, UserNote
from .serializers import CourseListSerializer, CourseDetailSerializer, MyCourseSerializer, UserNoteSerializer


class CourseViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        user = self.request.user
        queryset = Course.objects.filter(is_active=True)

        # بهینه‌سازی (حل N+1): برای حالت تکی (Detail)
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
        
        # برای حالت لیست معمولی
        return queryset.prefetch_related('lessons')

    # ==========================================
    # اندپوینت جدید: api/courses/list/my-courses/
    # ==========================================
    @action(detail=False, methods=['get'], url_path='my-courses', permission_classes=[IsAuthenticated])
    def my_courses(self, request):
        user = request.user
        
        # ۱. ابتدا پیدا می‌کنیم کاربر چه دوره‌هایی را شروع کرده است
        # کاربر هر دوره‌ای که حداقل یک `UserProgress` در جلساتش داشته باشد را شروع کرده است.
        # (اگر سیستم ثبت نام / خرید دوره مجزا دارید، می‌توانید از آن جدول فیلتر کنید)
        started_course_ids = UserProgress.objects.filter(
            user=user
        ).values_list('lesson__course_id', flat=True).distinct()

        # ۲. دوره‌ها را فیلتر کرده و با Prefetch بهینه‌سازی می‌کنیم
        lessons_prefetch = Prefetch(
            'lessons',
            queryset=Lesson.objects.prefetch_related(
                Prefetch(
                    'completed_by', 
                    queryset=UserProgress.objects.filter(user=user, is_completed=True), 
                    to_attr='user_progress'
                )
            )
        )
        
        # دوره‌های پیدا شده را می‌گیریم و دیتای جلساتش را برای محاسبه پیشرفت، از قبل بارگذاری (Preload) می‌کنیم
        courses = Course.objects.filter(
            id__in=started_course_ids, 
            is_active=True
        ).prefetch_related(lessons_prefetch)

        # ۳. پاس دادن به سریالایزر جدید
        serializer = MyCourseSerializer(courses, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)


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