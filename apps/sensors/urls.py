"""
URL Configuration para la app Sensors
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import SensorViewSet

# Router para los ViewSets
router = DefaultRouter()
router.register(r'sensors', SensorViewSet, basename='sensor')

urlpatterns = [
    path('', include(router.urls)),
]
