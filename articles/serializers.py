from rest_framework import serializers
from .models import Article
from core.utils import convert_to_shamsi # ایمپورت کردن تابع کمکی

class ArticleListSerializer(serializers.ModelSerializer):
    # ما فیلد created_at را اورراید (Overide) می‌کنیم تا رشته شمسی برگرداند
    created_at = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = ['id', 'title', 'summary', 'image', 'created_at']

    def get_created_at(self, obj):
        return convert_to_shamsi(obj.created_at)

class ArticleDetailSerializer(serializers.ModelSerializer):
    created_at = serializers.SerializerMethodField()

    class Meta:
        model = Article
        fields = '__all__'

    def get_created_at(self, obj):
        return convert_to_shamsi(obj.created_at)