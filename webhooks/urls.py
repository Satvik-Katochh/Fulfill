"""
URL configuration for webhooks app.
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import WebhookViewSet

router = DefaultRouter()
router.register(r'webhooks', WebhookViewSet, basename='webhook')

urlpatterns = [
    path('api/', include(router.urls)),
]

