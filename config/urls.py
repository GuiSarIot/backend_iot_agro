"""
URL configuration for iot_sensor_platform project.
"""

from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView
)

urlpatterns = [
    # Django Admin
    path('admin/', admin.site.urls),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # API Apps - Modular Structure
    path('api/', include('apps.accounts.urls')),  # /api/auth/, /api/users/, /api/roles/, /api/permisos/, /api/dashboard/
    path('api/', include('apps.sensors.urls')),   # /api/sensors/
    path('api/', include('apps.devices.urls')),   # /api/devices/
    path('api/', include('apps.readings.urls')),  # /api/readings/
    path('api/mqtt/', include('apps.mqtt.urls')),  # /api/mqtt/brokers/, /api/mqtt/credentials/, etc.
]
