"""
URL Configuration para la app MQTT
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    BrokerConfigViewSet, MQTTCredentialViewSet, MQTTTopicViewSet,
    DeviceMQTTConfigViewSet, test_mqtt_connection, device_mqtt_status,
    EMQXUserViewSet, EMQXACLViewSet
)

# Router para los ViewSets
router = DefaultRouter()
router.register(r'brokers', BrokerConfigViewSet, basename='mqtt-broker')
router.register(r'credentials', MQTTCredentialViewSet, basename='mqtt-credential')
router.register(r'topics', MQTTTopicViewSet, basename='mqtt-topic')
router.register(r'device-config', DeviceMQTTConfigViewSet, basename='mqtt-device-config')
router.register(r'emqx-users', EMQXUserViewSet, basename='emqx-user')
router.register(r'emqx-acl', EMQXACLViewSet, basename='emqx-acl')

urlpatterns = [
    # Endpoints adicionales
    path('test-connection/', test_mqtt_connection, name='mqtt-test-connection'),
    path('device-status/', device_mqtt_status, name='mqtt-device-status'),
    
    # Incluir las rutas del router
    path('', include(router.urls)),
]
