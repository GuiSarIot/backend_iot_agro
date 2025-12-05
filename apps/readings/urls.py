"""
URL Configuration para la app Readings
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import LecturaViewSet

# Router para los ViewSets
router = DefaultRouter()
router.register(r'readings', LecturaViewSet, basename='reading')

urlpatterns = [
    path('', include(router.urls)),
]
