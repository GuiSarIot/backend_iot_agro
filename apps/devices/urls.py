"""
URL Configuration para la app Devices
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import DispositivoViewSet

# Router para los ViewSets
router = DefaultRouter()
router.register(r'devices', DispositivoViewSet, basename='device')

urlpatterns = [
    path('', include(router.urls)),
]
