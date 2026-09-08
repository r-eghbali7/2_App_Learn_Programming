# articles/views.py
from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from rest_framework.filters import SearchFilter  # === اضافه شد ===
from .models import Article
from .serializers import ArticleListSerializer, ArticleDetailSerializer

class ArticleViewSet(viewsets.ReadOnlyModelViewSet):
    """
    فقط اجازه خواندن (GET) می‌دهد.
    """
    queryset = Article.objects.filter(is_active=True)
    permission_classes = [AllowAny]
    
    # === فعال‌سازی جستجو ===
    filter_backends = [SearchFilter]
    search_fields = ['title'] # فیلدهایی که در آن‌ها سرچ می‌شود

    def get_serializer_class(self):
        if self.action == 'list':
            return ArticleListSerializer
        return ArticleDetailSerializer