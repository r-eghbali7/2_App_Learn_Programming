from rest_framework import viewsets
from rest_framework.permissions import AllowAny
from .models import Article
from .serializers import ArticleListSerializer, ArticleDetailSerializer

class ArticleViewSet(viewsets.ReadOnlyModelViewSet):
    """
    فقط اجازه خواندن (GET) می‌دهد.
    """
    queryset = Article.objects.filter(is_active=True)
    permission_classes = [AllowAny]

    def get_serializer_class(self):
        if self.action == 'list':
            return ArticleListSerializer
        return ArticleDetailSerializer