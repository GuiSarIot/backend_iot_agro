"""
Serializers para la app Sensors
"""

from rest_framework import serializers
from .models import Sensor


class SensorSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Sensor
    """
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    created_by_username = serializers.CharField(
        source='created_by.username',
        read_only=True
    )
    
    class Meta:
        model = Sensor
        fields = [
            'id', 'nombre', 'tipo', 'tipo_display', 'unidad_medida',
            'rango_min', 'rango_max', 'estado', 'estado_display',
            'descripcion', 'mqtt_topic_suffix', 'publish_interval',
            'created_by', 'created_by_username',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_by', 'created_at', 'updated_at']
    
    def validate(self, attrs):
        rango_min = attrs.get('rango_min')
        rango_max = attrs.get('rango_max')
        
        # Si es una actualizacion, obtener los valores actuales si no se proporcionan nuevos
        if self.instance:
            rango_min = rango_min if rango_min is not None else self.instance.rango_min
            rango_max = rango_max if rango_max is not None else self.instance.rango_max
        
        if rango_min is not None and rango_max is not None:
            if rango_min >= rango_max:
                raise serializers.ValidationError(
                    "El rango minimo debe ser menor que el rango maximo."
                )
        
        return attrs
