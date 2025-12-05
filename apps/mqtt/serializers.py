"""
Serializers para la app MQTT
"""

from rest_framework import serializers
from .models import BrokerConfig, MQTTCredential, MQTTTopic, DeviceMQTTConfig


class BrokerConfigSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo BrokerConfig
    """
    protocol_display = serializers.CharField(source='get_protocol_display', read_only=True)
    # Ocultar password en lectura
    password = serializers.CharField(write_only=True, required=False, allow_blank=True, allow_null=True)
    
    class Meta:
        model = BrokerConfig
        fields = [
            'id', 'nombre', 'host', 'port', 'protocol', 'protocol_display',
            'username', 'password', 'keepalive', 'clean_session',
            'use_tls', 'ca_cert', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
        extra_kwargs = {
            'password': {'write_only': True}
        }


class MQTTCredentialSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo MQTTCredential
    """
    dispositivo_nombre = serializers.CharField(source='dispositivo.nombre', read_only=True)
    # Ocultar password y claves en lectura (solo mostrar que existen)
    password = serializers.CharField(write_only=True)
    client_key = serializers.CharField(write_only=True, required=False, allow_blank=True, allow_null=True)
    has_password = serializers.SerializerMethodField()
    has_cert = serializers.SerializerMethodField()
    
    class Meta:
        model = MQTTCredential
        fields = [
            'id', 'dispositivo', 'dispositivo_nombre', 'client_id',
            'username', 'password', 'has_password', 'use_device_cert',
            'client_cert', 'client_key', 'has_cert', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_has_password(self, obj):
        return bool(obj.password)
    
    def get_has_cert(self, obj):
        return bool(obj.client_cert and obj.client_key)


class MQTTCredentialDetailSerializer(MQTTCredentialSerializer):
    """
    Serializer con detalles completos de credenciales (solo para superusuarios)
    """
    password = serializers.CharField(read_only=True)
    client_key = serializers.CharField(read_only=True)
    
    class Meta(MQTTCredentialSerializer.Meta):
        fields = MQTTCredentialSerializer.Meta.fields
        read_only_fields = MQTTCredentialSerializer.Meta.read_only_fields


class MQTTTopicSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo MQTTTopic
    """
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    qos_display = serializers.CharField(source='get_qos_display', read_only=True)
    
    class Meta:
        model = MQTTTopic
        fields = [
            'id', 'nombre', 'topic_pattern', 'tipo', 'tipo_display',
            'qos', 'qos_display', 'retain', 'descripcion',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class DeviceMQTTConfigSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo DeviceMQTTConfig
    """
    dispositivo_nombre = serializers.CharField(source='dispositivo.nombre', read_only=True)
    broker_nombre = serializers.CharField(source='broker.nombre', read_only=True)
    publish_topic_nombre = serializers.CharField(source='publish_topic.nombre', read_only=True)
    connection_status_display = serializers.CharField(
        source='get_connection_status_display',
        read_only=True
    )
    qos_display = serializers.CharField(source='get_qos_display', read_only=True)
    
    class Meta:
        model = DeviceMQTTConfig
        fields = [
            'id', 'dispositivo', 'dispositivo_nombre', 'broker', 'broker_nombre',
            'publish_topic', 'publish_topic_nombre', 'subscribe_topics',
            'publish_interval', 'qos', 'qos_display', 'retain', 'auto_reconnect',
            'last_connection', 'connection_status', 'connection_status_display',
            'metadata_json', 'is_active', 'created_at', 'updated_at'
        ]
        read_only_fields = ['last_connection', 'created_at', 'updated_at']


class DeviceMQTTConfigDetailSerializer(serializers.ModelSerializer):
    """
    Serializer detallado con informacion anidada completa
    """
    dispositivo_nombre = serializers.CharField(source='dispositivo.nombre', read_only=True)
    broker_detail = BrokerConfigSerializer(source='broker', read_only=True)
    publish_topic_detail = MQTTTopicSerializer(source='publish_topic', read_only=True)
    subscribe_topics_detail = MQTTTopicSerializer(source='subscribe_topics', many=True, read_only=True)
    connection_status_display = serializers.CharField(
        source='get_connection_status_display',
        read_only=True
    )
    
    class Meta:
        model = DeviceMQTTConfig
        fields = [
            'id', 'dispositivo', 'dispositivo_nombre', 'broker', 'broker_detail',
            'publish_topic', 'publish_topic_detail', 'subscribe_topics',
            'subscribe_topics_detail', 'publish_interval', 'qos', 'retain',
            'auto_reconnect', 'last_connection', 'connection_status',
            'connection_status_display', 'metadata_json', 'is_active',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['last_connection', 'created_at', 'updated_at']


class TestMQTTConnectionSerializer(serializers.Serializer):
    """
    Serializer para probar conexion con el broker MQTT
    """
    broker_id = serializers.IntegerField(required=True)
    timeout = serializers.IntegerField(default=10, min_value=1, max_value=60)
    
    def validate_broker_id(self, value):
        try:
            BrokerConfig.objects.get(id=value, is_active=True)
        except BrokerConfig.DoesNotExist:
            raise serializers.ValidationError("El broker no existe o no esta activo.")
        return value
