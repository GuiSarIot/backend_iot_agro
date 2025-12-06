"""
Serializers para la app MQTT
"""

from rest_framework import serializers
from .models import BrokerConfig, MQTTCredential, MQTTTopic, DeviceMQTTConfig, EMQXUser, EMQXACL


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


class EMQXUserSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo EMQXUser
    Compatible con autenticación EMQX PostgreSQL
    """
    dispositivo_nombre = serializers.CharField(source='dispositivo.nombre', read_only=True)
    password = serializers.CharField(write_only=True, required=False)
    # No exponer password_hash ni salt en la API por seguridad
    acl_rules_count = serializers.SerializerMethodField()
    
    class Meta:
        model = EMQXUser
        fields = [
            'id', 'username', 'password', 'is_superuser',
            'dispositivo', 'dispositivo_nombre', 'acl_rules_count',
            'created'
        ]
        read_only_fields = ['created', 'acl_rules_count']
        extra_kwargs = {
            'password': {'write_only': True},
        }
    
    def get_acl_rules_count(self, obj):
        """Retorna el número de reglas ACL asociadas"""
        return obj.acl_rules.count()
    
    def create(self, validated_data):
        """
        Crea un nuevo usuario EMQX con hash de contraseña
        """
        password = validated_data.pop('password', None)
        user = EMQXUser(**validated_data)
        
        if password:
            user.set_password(password)
        
        user.save()
        return user
    
    def update(self, instance, validated_data):
        """
        Actualiza usuario EMQX, re-hasheando contraseña si se proporciona
        """
        password = validated_data.pop('password', None)
        
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if password:
            instance.set_password(password)
        
        instance.save()
        return instance


class EMQXACLSerializer(serializers.ModelSerializer):
    """
    Serializer para el modelo EMQXACL
    Compatible con autorización EMQX PostgreSQL
    """
    permission_display = serializers.CharField(source='get_permission_display', read_only=True)
    action_display = serializers.CharField(source='get_action_display', read_only=True)
    qos_display = serializers.CharField(source='get_qos_display', read_only=True)
    retain_display = serializers.CharField(source='get_retain_display', read_only=True)
    
    class Meta:
        model = EMQXACL
        fields = [
            'id', 'username', 'permission', 'permission_display',
            'action', 'action_display', 'topic', 'qos', 'qos_display',
            'retain', 'retain_display', 'emqx_user', 'created_at'
        ]
        read_only_fields = ['created_at']
    
    def validate_topic(self, value):
        """
        Valida el formato del topic MQTT
        """
        if not value:
            raise serializers.ValidationError("El topic no puede estar vacío")
        
        # Validar caracteres básicos de MQTT topic
        invalid_chars = ['+', '#']
        for i, char in enumerate(value):
            if char == '+':
                # '+' solo es válido como nivel completo
                if i > 0 and value[i-1] != '/':
                    raise serializers.ValidationError(
                        "El wildcard '+' debe ser un nivel completo del topic"
                    )
            elif char == '#':
                # '#' solo es válido al final
                if i != len(value) - 1:
                    raise serializers.ValidationError(
                        "El wildcard '#' solo puede estar al final del topic"
                    )
        
        return value
    
    def validate(self, data):
        """
        Validación cruzada de campos
        """
        # Si hay emqx_user, verificar que el username coincida
        if data.get('emqx_user'):
            if data['username'] != data['emqx_user'].username:
                raise serializers.ValidationError(
                    "El username debe coincidir con el usuario EMQX asociado"
                )
        
        return data


class EMQXUserDetailSerializer(EMQXUserSerializer):
    """
    Serializer detallado con reglas ACL incluidas
    """
    acl_rules = EMQXACLSerializer(many=True, read_only=True)
    
    class Meta(EMQXUserSerializer.Meta):
        fields = EMQXUserSerializer.Meta.fields + ['acl_rules']


class CreateEMQXUserWithACLSerializer(serializers.Serializer):
    """
    Serializer para crear usuario EMQX con reglas ACL en una sola operación
    """
    username = serializers.CharField(max_length=255)
    password = serializers.CharField(write_only=True, min_length=8)
    is_superuser = serializers.BooleanField(default=False)
    dispositivo_id = serializers.IntegerField(
        required=False,
        allow_null=True,
        help_text="ID del dispositivo IoT asociado (opcional)"
    )
    acl_rules = serializers.ListField(
        child=serializers.DictField(),
        required=False,
        help_text="Lista de reglas ACL a crear para este usuario"
    )
    
    def validate_dispositivo_id(self, value):
        """
        Valida que el dispositivo exista
        """
        if value is not None:
            from apps.devices.models import Dispositivo
            try:
                Dispositivo.objects.get(id=value)
            except Dispositivo.DoesNotExist:
                raise serializers.ValidationError("El dispositivo especificado no existe")
        return value
    
    def validate_acl_rules(self, value):
        """
        Valida la lista de reglas ACL
        """
        required_fields = ['permission', 'action', 'topic']
        for rule in value:
            for field in required_fields:
                if field not in rule:
                    raise serializers.ValidationError(
                        f"Cada regla ACL debe tener el campo '{field}'"
                    )
        return value
    
    def create(self, validated_data):
        """
        Crea usuario EMQX y sus reglas ACL de forma transaccional
        """
        from django.db import transaction
        from apps.devices.models import Dispositivo
        
        acl_rules_data = validated_data.pop('acl_rules', [])
        password = validated_data.pop('password')
        dispositivo_id = validated_data.pop('dispositivo_id', None)
        
        with transaction.atomic():
            # Obtener dispositivo si existe
            dispositivo = None
            if dispositivo_id:
                dispositivo = Dispositivo.objects.get(id=dispositivo_id)
            
            # Crear usuario EMQX
            user = EMQXUser(dispositivo=dispositivo, **validated_data)
            user.set_password(password)
            user.save()
            
            # Crear reglas ACL
            for rule_data in acl_rules_data:
                EMQXACL.objects.create(
                    username=user.username,
                    emqx_user=user,
                    **rule_data
                )
        
        return user
