"""
Serializers para la app Readings
"""

from rest_framework import serializers
from .models import Lectura
from apps.devices.models import DispositivoSensor


class LecturaSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Lectura
    """
    dispositivo_nombre = serializers.CharField(
        source='dispositivo.nombre',
        read_only=True
    )
    sensor_nombre = serializers.CharField(source='sensor.nombre', read_only=True)
    sensor_unidad = serializers.CharField(
        source='sensor.unidad_medida',
        read_only=True
    )
    
    class Meta:
        model = Lectura
        fields = [
            'id', 'dispositivo', 'dispositivo_nombre', 'sensor',
            'sensor_nombre', 'sensor_unidad', 'valor', 'timestamp',
            'metadata_json', 'mqtt_message_id', 'mqtt_qos', 'mqtt_retained'
        ]
        read_only_fields = ['timestamp']
    
    def validate(self, attrs):
        dispositivo = attrs.get('dispositivo')
        sensor = attrs.get('sensor')
        valor = attrs.get('valor')
        
        # Si es una actualizacion, obtener los valores actuales si no se proporcionan nuevos
        if self.instance:
            dispositivo = dispositivo or self.instance.dispositivo
            sensor = sensor or self.instance.sensor
            valor = valor if valor is not None else self.instance.valor
        
        # Validar que el sensor este asignado al dispositivo
        if dispositivo and sensor:
            if not DispositivoSensor.objects.filter(
                dispositivo=dispositivo,
                sensor=sensor,
                activo=True
            ).exists():
                raise serializers.ValidationError(
                    "El sensor no esta asignado a este dispositivo."
                )
        
        # Validar que el valor este dentro del rango del sensor
        if sensor and valor is not None:
            if valor < sensor.rango_min or valor > sensor.rango_max:
                raise serializers.ValidationError(
                    f"El valor {valor} esta fuera del rango permitido "
                    f"({sensor.rango_min} - {sensor.rango_max})."
                )
        
        return attrs


class LecturaBulkSerializer(serializers.Serializer):
    """
    Serializer para crear multiples lecturas a la vez
    """
    lecturas = LecturaSerializer(many=True)
    
    def create(self, validated_data):
        lecturas_data = validated_data['lecturas']
        lecturas = [Lectura(**lectura_data) for lectura_data in lecturas_data]
        return Lectura.objects.bulk_create(lecturas)
