"""
Serializers para la app Devices
"""

from rest_framework import serializers
from .models import Dispositivo, DispositivoSensor
from apps.sensors.serializers import SensorSerializer


class DispositivoSensorSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo DispositivoSensor
    """
    sensor_detail = SensorSerializer(source='sensor', read_only=True)
    dispositivo_nombre = serializers.CharField(
        source='dispositivo.nombre',
        read_only=True
    )
    sensor_nombre = serializers.CharField(source='sensor.nombre', read_only=True)
    
    class Meta:
        model = DispositivoSensor
        fields = [
            'id', 'dispositivo', 'dispositivo_nombre', 'sensor',
            'sensor_nombre', 'sensor_detail', 'configuracion_json',
            'fecha_asignacion', 'activo'
        ]
        read_only_fields = ['fecha_asignacion']


class DispositivoSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo Dispositivo
    """
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    connection_status_display = serializers.CharField(
        source='get_connection_status_display',
        read_only=True
    )
    operador_username = serializers.CharField(
        source='operador_asignado.username',
        read_only=True
    )
    sensores_asignados = DispositivoSensorSerializer(
        source='dispositivosensor_set',
        many=True,
        read_only=True
    )
    cantidad_sensores = serializers.SerializerMethodField()
    
    class Meta:
        model = Dispositivo
        fields = [
            'id', 'nombre', 'tipo', 'tipo_display', 'identificador_unico',
            'ubicacion', 'estado', 'estado_display', 'descripcion',
            'mqtt_enabled', 'mqtt_client_id', 'last_seen', 'connection_status',
            'connection_status_display', 'operador_asignado', 'operador_username',
            'sensores_asignados', 'cantidad_sensores', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_cantidad_sensores(self, obj):
        return obj.sensores.count()
    
    def validate_identificador_unico(self, value):
        # Verificar que el identificador unico no exista ya
        if self.instance:
            # Si es una actualizacion, excluir el propio dispositivo
            if Dispositivo.objects.exclude(id=self.instance.id).filter(
                identificador_unico=value
            ).exists():
                raise serializers.ValidationError(
                    "Ya existe un dispositivo con este identificador unico."
                )
        else:
            # Si es una creacion
            if Dispositivo.objects.filter(identificador_unico=value).exists():
                raise serializers.ValidationError(
                    "Ya existe un dispositivo con este identificador unico."
                )
        return value
    
    def validate_mqtt_client_id(self, value):
        if value:
            # Verificar que el mqtt_client_id no exista ya
            if self.instance:
                if Dispositivo.objects.exclude(id=self.instance.id).filter(
                    mqtt_client_id=value
                ).exists():
                    raise serializers.ValidationError(
                        "Ya existe un dispositivo con este Client ID MQTT."
                    )
            else:
                if Dispositivo.objects.filter(mqtt_client_id=value).exists():
                    raise serializers.ValidationError(
                        "Ya existe un dispositivo con este Client ID MQTT."
                    )
        return value


class AsignarSensorDispositivoSerializer(serializers.Serializer):
    """
    Serializer para asignar un sensor a un dispositivo
    """
    sensor_id = serializers.IntegerField(required=True)
    configuracion_json = serializers.JSONField(required=False, default=dict)
    
    def validate_sensor_id(self, value):
        from apps.sensors.models import Sensor
        try:
            Sensor.objects.get(id=value)
        except Sensor.DoesNotExist:
            raise serializers.ValidationError("El sensor no existe.")
        return value


class AsignarOperadorDispositivoSerializer(serializers.Serializer):
    """
    Serializer para asignar un operador a un dispositivo
    """
    operador_id = serializers.IntegerField(required=True)
    
    def validate_operador_id(self, value):
        from apps.accounts.models import CustomUser
        try:
            user = CustomUser.objects.get(id=value)
            if user.rol and user.rol.nombre != 'operador':
                raise serializers.ValidationError(
                    "El usuario debe tener el rol de operador."
                )
        except CustomUser.DoesNotExist:
            raise serializers.ValidationError("El usuario no existe.")
        return value
