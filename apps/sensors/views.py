"""
Views y ViewSets para la app Sensors
"""

from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
import logging

from .models import Sensor
from .serializers import SensorSerializer
from apps.accounts.permissions import CanManageSensors

logger = logging.getLogger(__name__)


class SensorViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar Sensores
    """
    queryset = Sensor.objects.select_related('created_by').all()
    serializer_class = SensorSerializer
    permission_classes = [IsAuthenticated, CanManageSensors]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'tipo', 'descripcion']
    ordering_fields = ['nombre', 'tipo', 'created_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtrar por tipo de sensor
        tipo = self.request.query_params.get('tipo', None)
        if tipo:
            queryset = queryset.filter(tipo=tipo)
        
        # Filtrar por estado
        estado = self.request.query_params.get('estado', None)
        if estado:
            queryset = queryset.filter(estado=estado)
        
        # Filtrar sensores con MQTT habilitado
        mqtt_enabled = self.request.query_params.get('mqtt_enabled', None)
        if mqtt_enabled is not None:
            queryset = queryset.exclude(mqtt_topic_suffix__isnull=True)
        
        return queryset
    
    def perform_create(self, serializer):
        logger.info(f"Creando sensor: {serializer.validated_data.get('nombre')}")
        serializer.save(created_by=self.request.user)
    
    def perform_update(self, serializer):
        logger.info(f"Actualizando sensor: {serializer.instance.nombre}")
        serializer.save()
    
    @action(detail=False, methods=['get'])
    def available(self, request):
        """
        Obtener sensores disponibles para asignar (activos)
        GET /api/sensors/available/
        """
        sensores = self.queryset.filter(estado='activo')
        serializer = self.get_serializer(sensores, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def tipos(self, request):
        """
        Obtener lista de tipos de sensores disponibles
        GET /api/sensors/tipos/
        """
        tipos = [{'value': t[0], 'label': t[1]} for t in Sensor.TIPO_SENSOR_CHOICES]
        return Response(tipos)
    
    @action(detail=False, methods=['get'])
    def mqtt_enabled(self, request):
        """
        Obtener sensores con MQTT configurado
        GET /api/sensors/mqtt-enabled/
        """
        sensores = self.queryset.filter(
            estado='activo'
        ).exclude(mqtt_topic_suffix__isnull=True)
        serializer = self.get_serializer(sensores, many=True)
        return Response(serializer.data)
