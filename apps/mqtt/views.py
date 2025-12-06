"""
Views y ViewSets para la app MQTT
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
import logging

from .models import BrokerConfig, MQTTCredential, MQTTTopic, DeviceMQTTConfig, EMQXUser, EMQXACL
from .serializers import (
    BrokerConfigSerializer, MQTTCredentialSerializer, MQTTCredentialDetailSerializer,
    MQTTTopicSerializer, DeviceMQTTConfigSerializer, DeviceMQTTConfigDetailSerializer,
    TestMQTTConnectionSerializer, EMQXUserSerializer, EMQXUserDetailSerializer,
    EMQXACLSerializer, CreateEMQXUserWithACLSerializer
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


class EMQXUserViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar usuarios EMQX (autenticación MQTT)
    """
    queryset = EMQXUser.objects.select_related('dispositivo').prefetch_related('acl_rules').all()
    permission_classes = [IsAuthenticated, CanManageMQTT]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'dispositivo__nombre']
    ordering_fields = ['username', 'created']
    ordering = ['-created']
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return EMQXUserDetailSerializer
        elif self.action == 'create_with_acl':
            return CreateEMQXUserWithACLSerializer
        return EMQXUserSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtrar por superusuario
        is_superuser = self.request.query_params.get('is_superuser', None)
        if is_superuser is not None:
            queryset = queryset.filter(is_superuser=is_superuser.lower() == 'true')
        
        # Filtrar por dispositivo
        dispositivo_id = self.request.query_params.get('dispositivo', None)
        if dispositivo_id:
            queryset = queryset.filter(dispositivo_id=dispositivo_id)
        
        return queryset
    
    def perform_create(self, serializer):
        logger.info(f"Creando usuario EMQX: {serializer.validated_data.get('username')}")
        serializer.save()
    
    @action(detail=True, methods=['get'])
    def credentials(self, request, pk=None):
        """
        Obtener credenciales de usuario EMQX (solo superusuarios)
        GET /api/mqtt/emqx-users/{id}/credentials/
        """
        if not request.user.is_superuser:
            return Response({
                'error': 'Solo superusuarios pueden ver credenciales completas'
            }, status=status.HTTP_403_FORBIDDEN)
        
        user = self.get_object()
        return Response({
            'username': user.username,
            'password_hash': user.password_hash,
            'salt': user.salt,
            'is_superuser': user.is_superuser,
            'dispositivo': user.dispositivo.nombre if user.dispositivo else None,
            'created': user.created
        })
    
    @action(detail=True, methods=['post'])
    def change_password(self, request, pk=None):
        """
        Cambiar contraseña de usuario EMQX
        POST /api/mqtt/emqx-users/{id}/change_password/
        Body: {"password": "nueva_password"}
        """
        user = self.get_object()
        new_password = request.data.get('password')
        
        if not new_password:
            return Response({
                'error': 'Se requiere el campo "password"'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if len(new_password) < 8:
            return Response({
                'error': 'La contraseña debe tener al menos 8 caracteres'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user.set_password(new_password)
        user.save()
        
        logger.info(f"Contraseña actualizada para usuario EMQX: {user.username}")
        
        return Response({
            'message': f'Contraseña actualizada exitosamente para {user.username}'
        })
    
    @action(detail=False, methods=['post'])
    def create_with_acl(self, request):
        """
        Crear usuario EMQX con reglas ACL en una sola operación
        POST /api/mqtt/emqx-users/create_with_acl/
        """
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            logger.info(
                f"Usuario EMQX creado con reglas ACL: {user.username} "
                f"({user.acl_rules.count()} reglas)"
            )
            return Response(
                EMQXUserDetailSerializer(user).data,
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EMQXACLViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar reglas ACL de EMQX (autorización MQTT)
    """
    queryset = EMQXACL.objects.select_related('emqx_user').all()
    serializer_class = EMQXACLSerializer
    permission_classes = [IsAuthenticated, CanManageMQTT]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'topic']
    ordering_fields = ['username', 'topic', 'created_at']
    ordering = ['username', 'topic']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtrar por username
        username = self.request.query_params.get('username', None)
        if username:
            queryset = queryset.filter(username=username)
        
        # Filtrar por acción
        action = self.request.query_params.get('action', None)
        if action:
            queryset = queryset.filter(action=action)
        
        # Filtrar por permiso
        permission = self.request.query_params.get('permission', None)
        if permission:
            queryset = queryset.filter(permission=permission)
        
        # Filtrar por usuario EMQX
        emqx_user_id = self.request.query_params.get('emqx_user', None)
        if emqx_user_id:
            queryset = queryset.filter(emqx_user_id=emqx_user_id)
        
        return queryset
    
    def perform_create(self, serializer):
        logger.info(
            f"Creando regla ACL: {serializer.validated_data.get('username')} - "
            f"{serializer.validated_data.get('action')} on {serializer.validated_data.get('topic')}"
        )
        serializer.save()
    
    @action(detail=False, methods=['get'])
    def by_device(self, request):
        """
        Obtener reglas ACL por dispositivo
        GET /api/mqtt/emqx-acl/by_device/?dispositivo_id=1
        """
        dispositivo_id = request.query_params.get('dispositivo_id')
        
        if not dispositivo_id:
            return Response({
                'error': 'Se requiere el parámetro dispositivo_id'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            dispositivo = Dispositivo.objects.get(id=dispositivo_id)
        except Dispositivo.DoesNotExist:
            return Response({
                'error': 'Dispositivo no encontrado'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Buscar usuario EMQX del dispositivo
        try:
            emqx_user = EMQXUser.objects.get(dispositivo=dispositivo)
            acl_rules = EMQXACL.objects.filter(emqx_user=emqx_user)
            serializer = self.get_serializer(acl_rules, many=True)
            
            return Response({
                'dispositivo': dispositivo.nombre,
                'emqx_username': emqx_user.username,
                'acl_rules_count': acl_rules.count(),
                'acl_rules': serializer.data
            })
        except EMQXUser.DoesNotExist:
            return Response({
                'error': 'El dispositivo no tiene usuario EMQX asociado'
            }, status=status.HTTP_404_NOT_FOUND)
