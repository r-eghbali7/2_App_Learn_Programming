from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PlanViewSet, MySubscriptionViewSet

router = DefaultRouter()
router.register(r'plans', PlanViewSet, basename='plan')
router.register(r'my', MySubscriptionViewSet, basename='my-subscription')

urlpatterns = [
    path('', include(router.urls)),
]