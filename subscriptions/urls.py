from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PaymentRequestView, PaymentVerifyView, PlanViewSet, MySubscriptionViewSet

router = DefaultRouter()
router.register(r'plans', PlanViewSet, basename='plan')
router.register(r'my', MySubscriptionViewSet, basename='my-subscription')

urlpatterns = [
    path('', include(router.urls)),
    path('request-payment/', PaymentRequestView.as_view(), name='request-payment'),
    path('verify-payment/', PaymentVerifyView.as_view(), name='verify-payment'),
]