"""
Views y ViewSets para la app Readings
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Avg, Max, Min, Count
import logging

from .models import Lectura
from .serializers import LecturaSerializer, LecturaBulkSerializer
from apps.accounts.permissions import CanCreateReadings

logger = logging.getLogger(__name__)


class LecturaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar Lecturas de sensores
    """
    queryset = Lectura.objects.select_related(
        'dispositivo', 'sensor'
    ).all()
    serializer_class = LecturaSerializer
    permission_classes = [IsAuthenticated, CanCreateReadings]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['timestamp']
    ordering = ['-timestamp']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Si el usuario es operador, solo ver lecturas de sus dispositivos
        if not self.request.user.is_superuser:
            if self.request.user.rol and self.request.user.rol.nombre == 'operador':
                queryset = queryset.filter(
                    dispositivo__operador_asignado=self.request.user
                )
        
        # Filtrar por dispositivo
        dispositivo_id = self.request.query_params.get('dispositivo', None)
        if dispositivo_id:
            queryset = queryset.filter(dispositivo_id=dispositivo_id)
        
        # Filtrar por sensor
        sensor_id = self.request.query_params.get('sensor', None)
        if sensor_id:
            queryset = queryset.filter(sensor_id=sensor_id)
        
        # Filtrar por rango de fechas
        fecha_inicio = self.request.query_params.get('fecha_inicio', None)
        fecha_fin = self.request.query_params.get('fecha_fin', None)
        
        if fecha_inicio:
            queryset = queryset.filter(timestamp__gte=fecha_inicio)
        if fecha_fin:
            queryset = queryset.filter(timestamp__lte=fecha_fin)
        
        # Filtrar lecturas MQTT
        mqtt_only = self.request.query_params.get('mqtt_only', None)
        if mqtt_only is not None:
            queryset = queryset.exclude(mqtt_message_id__isnull=True)
        
        return queryset
    
    def perform_create(self, serializer):
        logger.info(f"Creando lectura para sensor: {serializer.validated_data.get('sensor')}")
        serializer.save()
    
    @action(detail=False, methods=['post'])
    def bulk(self, request):
        """
        Crear multiples lecturas a la vez
        POST /api/readings/bulk/
        Body: {"lecturas": [{...}, {...}, ...]}
        """
        serializer = LecturaBulkSerializer(data=request.data)
        
        if serializer.is_valid():
            lecturas = serializer.save()
            logger.info(f"Creadas {len(lecturas)} lecturas en bulk")
            
            return Response({
                'message': f'{len(lecturas)} lecturas creadas exitosamente',
                'count': len(lecturas)
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """
        Obtener estadisticas de lecturas
        GET /api/readings/estadisticas/
        """
        dispositivo_id = request.query_params.get('dispositivo', None)
        sensor_id = request.query_params.get('sensor', None)
        
        queryset = self.get_queryset()
        
        if dispositivo_id:
            queryset = queryset.filter(dispositivo_id=dispositivo_id)
        if sensor_id:
            queryset = queryset.filter(sensor_id=sensor_id)
        
        stats = queryset.aggregate(
            total=Count('id'),
            promedio=Avg('valor'),
            maximo=Max('valor'),
            minimo=Min('valor')
        )
        
        # Agregar conteo de lecturas MQTT
        mqtt_count = queryset.exclude(mqtt_message_id__isnull=True).count()
        stats['lecturas_mqtt'] = mqtt_count
        
        return Response(stats)
    
    @action(detail=False, methods=['get'])
    def ultimas(self, request):
        """
        Obtener las ultimas N lecturas
        GET /api/readings/ultimas/?limit=10
        """
        limit = int(request.query_params.get('limit', 10))
        if limit > 100:
            limit = 100
        
        queryset = self.get_queryset()[:limit]
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
