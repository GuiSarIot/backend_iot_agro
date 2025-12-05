"""
Views y ViewSets para la app MQTT
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
import logging

from .models import BrokerConfig, MQTTCredential, MQTTTopic, DeviceMQTTConfig
from .serializers import (
    BrokerConfigSerializer, MQTTCredentialSerializer, MQTTCredentialDetailSerializer,
    MQTTTopicSerializer, DeviceMQTTConfigSerializer, DeviceMQTTConfigDetailSerializer,
    TestMQTTConnectionSerializer
)
from apps.accounts.permissions import CanManageMQTT, CanViewMQTTCredentials
from apps.devices.models import Dispositivo

logger = logging.getLogger(__name__)


class BrokerConfigViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar configuraciones de Brokers MQTT
    """
    queryset = BrokerConfig.objects.all()
    serializer_class = BrokerConfigSerializer
    permission_classes = [IsAuthenticated, CanManageMQTT]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'host']
    ordering_fields = ['nombre', 'created_at']
    ordering = ['-is_active', 'nombre']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtrar solo activos
        active_only = self.request.query_params.get('active_only', None)
        if active_only is not None:
            queryset = queryset.filter(is_active=True)
        
        # Filtrar por protocolo
        protocol = self.request.query_params.get('protocol', None)
        if protocol:
            queryset = queryset.filter(protocol=protocol)
        
        return queryset
    
    def perform_create(self, serializer):
        logger.info(f"Creando broker MQTT: {serializer.validated_data.get('nombre')}")
        serializer.save()
    
    def perform_update(self, serializer):
        logger.info(f"Actualizando broker MQTT: {serializer.instance.nombre}")
        serializer.save()
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """
        Activar un broker
        POST /api/mqtt/brokers/{id}/activate/
        """
        broker = self.get_object()
        broker.is_active = True
        broker.save()
        logger.info(f"Broker activado: {broker.nombre}")
        return Response({
            'message': f'Broker {broker.nombre} activado exitosamente'
        })
    
    @action(detail=True, methods=['post'])
    def deactivate(self, request, pk=None):
        """
        Desactivar un broker
        POST /api/mqtt/brokers/{id}/deactivate/
        """
        broker = self.get_object()
        broker.is_active = False
        broker.save()
        logger.info(f"Broker desactivado: {broker.nombre}")
        return Response({
            'message': f'Broker {broker.nombre} desactivado exitosamente'
        })


class MQTTCredentialViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar credenciales MQTT
    """
    queryset = MQTTCredential.objects.select_related('dispositivo').all()
    permission_classes = [IsAuthenticated, CanViewMQTTCredentials]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['client_id', 'username', 'dispositivo__nombre']
    ordering_fields = ['created_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        # Superusuarios pueden ver credenciales completas
        if self.request.user.is_superuser and self.action == 'retrieve':
            return MQTTCredentialDetailSerializer
        return MQTTCredentialSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Operadores solo ven credenciales de sus dispositivos
        if not self.request.user.is_superuser:
            if self.request.user.rol and self.request.user.rol.nombre == 'operador':
                queryset = queryset.filter(
                    dispositivo__operador_asignado=self.request.user
                )
        
        # Filtrar por dispositivo
        dispositivo_id = self.request.query_params.get('dispositivo', None)
        if dispositivo_id:
            queryset = queryset.filter(dispositivo_id=dispositivo_id)
        
        # Filtrar solo activos
        active_only = self.request.query_params.get('active_only', None)
        if active_only is not None:
            queryset = queryset.filter(is_active=True)
        
        return queryset
    
    def perform_create(self, serializer):
        logger.info(f"Creando credencial MQTT: {serializer.validated_data.get('client_id')}")
        serializer.save()
    
    def perform_update(self, serializer):
        logger.info(f"Actualizando credencial MQTT: {serializer.instance.client_id}")
        serializer.save()


class MQTTTopicViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar topics MQTT
    """
    queryset = MQTTTopic.objects.all()
    serializer_class = MQTTTopicSerializer
    permission_classes = [IsAuthenticated, CanManageMQTT]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'topic_pattern', 'descripcion']
    ordering_fields = ['nombre', 'created_at']
    ordering = ['nombre']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtrar por tipo
        tipo = self.request.query_params.get('tipo', None)
        if tipo:
            queryset = queryset.filter(tipo=tipo)
        
        # Filtrar por QoS
        qos = self.request.query_params.get('qos', None)
        if qos is not None:
            queryset = queryset.filter(qos=int(qos))
        
        return queryset
    
    def perform_create(self, serializer):
        logger.info(f"Creando topic MQTT: {serializer.validated_data.get('nombre')}")
        serializer.save()
    
    def perform_update(self, serializer):
        logger.info(f"Actualizando topic MQTT: {serializer.instance.nombre}")
        serializer.save()
    
    @action(detail=False, methods=['get'])
    def publish_topics(self, request):
        """
        Obtener topics de publicacion
        GET /api/mqtt/topics/publish-topics/
        """
        topics = self.queryset.filter(tipo__in=['publish', 'both'])
        serializer = self.get_serializer(topics, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def subscribe_topics(self, request):
        """
        Obtener topics de suscripcion
        GET /api/mqtt/topics/subscribe-topics/
        """
        topics = self.queryset.filter(tipo__in=['subscribe', 'both'])
        serializer = self.get_serializer(topics, many=True)
        return Response(serializer.data)


class DeviceMQTTConfigViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar configuraciones MQTT de dispositivos
    """
    queryset = DeviceMQTTConfig.objects.select_related(
        'dispositivo', 'broker', 'publish_topic'
    ).prefetch_related('subscribe_topics').all()
    permission_classes = [IsAuthenticated, CanManageMQTT]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['dispositivo__nombre', 'broker__nombre']
    ordering_fields = ['last_connection', 'created_at']
    ordering = ['-last_connection']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return DeviceMQTTConfigDetailSerializer
        return DeviceMQTTConfigSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Operadores solo ven configuraciones de sus dispositivos
        if not self.request.user.is_superuser:
            if self.request.user.rol and self.request.user.rol.nombre == 'operador':
                queryset = queryset.filter(
                    dispositivo__operador_asignado=self.request.user
                )
        
        # Filtrar por dispositivo
        dispositivo_id = self.request.query_params.get('dispositivo', None)
        if dispositivo_id:
            queryset = queryset.filter(dispositivo_id=dispositivo_id)
        
        # Filtrar por broker
        broker_id = self.request.query_params.get('broker', None)
        if broker_id:
            queryset = queryset.filter(broker_id=broker_id)
        
        # Filtrar por estado de conexion
        connection_status = self.request.query_params.get('connection_status', None)
        if connection_status:
            queryset = queryset.filter(connection_status=connection_status)
        
        # Filtrar solo activos
        active_only = self.request.query_params.get('active_only', None)
        if active_only is not None:
            queryset = queryset.filter(is_active=True)
        
        return queryset
    
    def perform_create(self, serializer):
        logger.info(f"Creando config MQTT para dispositivo: {serializer.validated_data.get('dispositivo')}")
        serializer.save()
    
    def perform_update(self, serializer):
        logger.info(f"Actualizando config MQTT: {serializer.instance.dispositivo.nombre}")
        serializer.save()
    
    @action(detail=True, methods=['post'])
    def update_connection_status(self, request, pk=None):
        """
        Actualizar estado de conexion
        POST /api/mqtt/device-config/{id}/update-connection-status/
        Body: {"status": "connected|disconnected|error"}
        """
        config = self.get_object()
        new_status = request.data.get('status')
        
        if new_status not in ['connected', 'disconnected', 'error']:
            return Response({
                'error': 'Estado invalido. Use: connected, disconnected o error'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        config.connection_status = new_status
        if new_status == 'connected':
            from django.utils import timezone
            config.last_connection = timezone.now()
        config.save()
        
        # Actualizar tambien el dispositivo
        config.dispositivo.connection_status = 'online' if new_status == 'connected' else 'offline'
        config.dispositivo.last_seen = config.last_connection
        config.dispositivo.save()
        
        logger.info(f"Estado de conexion actualizado: {config.dispositivo.nombre} -> {new_status}")
        
        return Response({
            'message': 'Estado de conexion actualizado',
            'config': DeviceMQTTConfigSerializer(config).data
        })


# ============ Vistas adicionales ============

@api_view(['POST'])
@permission_classes([IsAuthenticated, CanManageMQTT])
def test_mqtt_connection(request):
    """
    Probar conexion con el broker MQTT
    POST /api/mqtt/test-connection/
    Body: {"broker_id": int, "timeout": 10}
    """
    serializer = TestMQTTConnectionSerializer(data=request.data)
    
    if serializer.is_valid():
        broker_id = serializer.validated_data['broker_id']
        serializer.validated_data.get('timeout', 10)
        
        try:
            broker = BrokerConfig.objects.get(id=broker_id)
        except BrokerConfig.DoesNotExist:
            return Response({
                'error': 'El broker no existe'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Aqui se implementaria la logica real de conexion
        # Por ahora retornamos un mock
        logger.info(f"Probando conexion con broker: {broker.nombre}")
        
        return Response({
            'success': True,
            'message': f'Conexion al broker {broker.nombre} exitosa',
            'broker': {
                'nombre': broker.nombre,
                'host': broker.host,
                'port': broker.port,
                'protocol': broker.protocol
            }
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def device_mqtt_status(request):
    """
    Obtener estado de conexion MQTT de dispositivos
    GET /api/mqtt/device-status/
    """
    # Operadores solo ven sus dispositivos
    dispositivos = Dispositivo.objects.filter(mqtt_enabled=True)
    
    if not request.user.is_superuser:
        if request.user.rol and request.user.rol.nombre == 'operador':
            dispositivos = dispositivos.filter(operador_asignado=request.user)
    
    # Obtener estadisticas
    total = dispositivos.count()
    online = dispositivos.filter(connection_status='online').count()
    offline = dispositivos.filter(connection_status='offline').count()
    error = dispositivos.filter(connection_status='error').count()
    
    return Response({
        'total_mqtt_devices': total,
        'online': online,
        'offline': offline,
        'error': error,
        'percentage_online': round((online / total * 100) if total > 0 else 0, 2)
    })
