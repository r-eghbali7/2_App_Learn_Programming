from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status

from .models import Banner
from .serializers import BannerSerializer, UserProfileSerializer
from courses.models import Course
from courses.serializers import CourseListSerializer
from articles.models import Article
from articles.serializers import ArticleListSerializer

class HomeDashboardView(APIView):
    """
    دریافت تمام اطلاعات مورد نیاز برای صفحه اول اپلیکیشن در یک درخواست
    """
    permission_classes = [AllowAny]

    def get(self, request):
        banners = Banner.objects.filter(is_active=True)[:5]
        # ۵ دوره آخر
        latest_courses = Course.objects.filter(is_active=True).order_by('-created_at')[:5]
        # ۵ مقاله آخر
        latest_articles = Article.objects.filter(is_active=True).order_by('-created_at')[:5]

        # ارسال context={'request': request} برای ساخته شدن درست URL کامل عکس‌ها (Media)
        context = {'request': request}
        
        return Response({
            'banners': BannerSerializer(banners, many=True, context=context).data,
            'latest_courses': CourseListSerializer(latest_courses, many=True, context=context).data,
            'latest_articles': ArticleListSerializer(latest_articles, many=True, context=context).data,
        }, status=status.HTTP_200_OK)


class UserProfileView(APIView):
    """
    مشاهده و ویرایش اطلاعات پروفایل کاربری که لاگین کرده است
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)

    def put(self, request):
        serializer = UserProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)