"""
Views y ViewSets para la app Devices
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
import logging

from .models import Dispositivo, DispositivoSensor
from .serializers import (
    DispositivoSerializer, DispositivoSensorSerializer,
    AsignarSensorDispositivoSerializer, AsignarOperadorDispositivoSerializer
)
from apps.accounts.permissions import CanManageDevices, IsSuperuser
from apps.accounts.models import CustomUser
from apps.sensors.models import Sensor

logger = logging.getLogger(__name__)


class DispositivoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar Dispositivos
    """
    queryset = Dispositivo.objects.select_related('operador_asignado').prefetch_related(
        'sensores', 'dispositivosensor_set__sensor'
    ).all()
    serializer_class = DispositivoSerializer
    permission_classes = [IsAuthenticated, CanManageDevices]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'tipo', 'identificador_unico', 'ubicacion']
    ordering_fields = ['nombre', 'tipo', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Si el usuario es operador, solo ver sus dispositivos asignados
        if not self.request.user.is_superuser:
            if self.request.user.rol and self.request.user.rol.nombre == 'operador':
                queryset = queryset.filter(operador_asignado=self.request.user)
        
        # Filtrar por tipo
        tipo = self.request.query_params.get('tipo', None)
        if tipo:
            queryset = queryset.filter(tipo=tipo)
        
        # Filtrar por estado
        estado = self.request.query_params.get('estado', None)
        if estado:
            queryset = queryset.filter(estado=estado)
        
        # Filtrar por operador
        operador_id = self.request.query_params.get('operador', None)
        if operador_id:
            queryset = queryset.filter(operador_asignado_id=operador_id)
        
        # Filtrar por MQTT habilitado
        mqtt_enabled = self.request.query_params.get('mqtt_enabled', None)
        if mqtt_enabled is not None:
            mqtt_val = mqtt_enabled.lower() in ['true', '1', 'yes']
            queryset = queryset.filter(mqtt_enabled=mqtt_val)
        
        # Filtrar por estado de conexion
        connection_status = self.request.query_params.get('connection_status', None)
        if connection_status:
            queryset = queryset.filter(connection_status=connection_status)
        
        return queryset
    
    def perform_create(self, serializer):
        logger.info(f"Creando dispositivo: {serializer.validated_data.get('nombre')}")
        serializer.save()
    
    def perform_update(self, serializer):
        logger.info(f"Actualizando dispositivo: {serializer.instance.nombre}")
        serializer.save()
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, CanManageDevices])
    def assign_sensor(self, request, pk=None):
        """
        Asignar un sensor a un dispositivo
        POST /api/devices/{id}/assign-sensor/
        Body: {"sensor_id": int, "configuracion_json": {}}
        """
        dispositivo = self.get_object()
        serializer = AsignarSensorDispositivoSerializer(data=request.data)
        
        if serializer.is_valid():
            sensor_id = serializer.validated_data['sensor_id']
            configuracion_json = serializer.validated_data.get('configuracion_json', {})
            
            try:
                sensor = Sensor.objects.get(id=sensor_id)
            except Sensor.DoesNotExist:
                return Response({
                    'error': 'El sensor no existe'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Verificar si ya existe la asignacion
            if DispositivoSensor.objects.filter(
                dispositivo=dispositivo,
                sensor=sensor
            ).exists():
                return Response({
                    'error': 'El sensor ya esta asignado a este dispositivo'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Crear la asignacion
            asignacion = DispositivoSensor.objects.create(
                dispositivo=dispositivo,
                sensor=sensor,
                configuracion_json=configuracion_json
            )
            
            logger.info(f"Sensor {sensor.nombre} asignado a dispositivo {dispositivo.nombre}")
            
            return Response({
                'message': 'Sensor asignado exitosamente',
                'asignacion': DispositivoSensorSerializer(asignacion).data
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsSuperuser])
    def assign_operator(self, request, pk=None):
        """
        Asignar un operador a un dispositivo
        POST /api/devices/{id}/assign-operator/
        Body: {"operador_id": int}
        """
        dispositivo = self.get_object()
        serializer = AsignarOperadorDispositivoSerializer(data=request.data)
        
        if serializer.is_valid():
            operador_id = serializer.validated_data['operador_id']
            
            try:
                operador = CustomUser.objects.get(id=operador_id)
            except CustomUser.DoesNotExist:
                return Response({
                    'error': 'El operador no existe'
                }, status=status.HTTP_404_NOT_FOUND)
            
            dispositivo.operador_asignado = operador
            dispositivo.save()
            
            logger.info(f"Operador {operador.username} asignado a dispositivo {dispositivo.nombre}")
            
            return Response({
                'message': 'Operador asignado exitosamente',
                'dispositivo': DispositivoSerializer(dispositivo).data
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['delete'])
    def remove_sensor(self, request, pk=None):
        """
        Remover un sensor de un dispositivo
        DELETE /api/devices/{id}/remove-sensor/?sensor_id=X
        """
        dispositivo = self.get_object()
        sensor_id = request.query_params.get('sensor_id', None)
        
        if not sensor_id:
            return Response({
                'error': 'Se requiere el parametro sensor_id'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            asignacion = DispositivoSensor.objects.get(
                dispositivo=dispositivo,
                sensor_id=sensor_id
            )
            asignacion.delete()
            
            logger.info(f"Sensor removido de dispositivo {dispositivo.nombre}")
            
            return Response({
                'message': 'Sensor removido exitosamente'
            })
        except DispositivoSensor.DoesNotExist:
            return Response({
                'error': 'La asignacion no existe'
            }, status=status.HTTP_404_NOT_FOUND)
    
    @action(detail=False, methods=['get'])
    def tipos(self, request):
        """
        Obtener lista de tipos de dispositivos disponibles
        GET /api/devices/tipos/
        """
        tipos = [{'value': t[0], 'label': t[1]} for t in Dispositivo.TIPO_DISPOSITIVO_CHOICES]
        return Response(tipos)
    
    @action(detail=False, methods=['get'])
    def mqtt_devices(self, request):
        """
        Obtener dispositivos con MQTT habilitado
        GET /api/devices/mqtt-devices/
        """
        dispositivos = self.get_queryset().filter(mqtt_enabled=True)
        serializer = self.get_serializer(dispositivos, many=True)
        return Response(serializer.data)
