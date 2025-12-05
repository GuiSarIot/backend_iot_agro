"""
Modelos de la app MQTT - Configuración MQTT/EMQX
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class BrokerConfig(models.Model):
    """
    Configuración del Broker MQTT (EMQX)
    """
    PROTOCOL_CHOICES = [
        ('mqtt', 'MQTT'),
        ('mqtts', 'MQTT over TLS'),
        ('ws', 'WebSocket'),
        ('wss', 'WebSocket Secure'),
    ]
    
    nombre = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Nombre',
        help_text='Nombre identificador de la configuración del broker'
    )
    host = models.CharField(
        max_length=255,
        verbose_name='Host',
        help_text='Dirección del broker MQTT (ej: localhost, broker.emqx.io)'
    )
    port = models.IntegerField(
        default=1883,
        verbose_name='Puerto',
        validators=[MinValueValidator(1), MaxValueValidator(65535)],
        help_text='Puerto del broker (1883 para MQTT, 8883 para MQTTS)'
    )
    protocol = models.CharField(
        max_length=10,
        choices=PROTOCOL_CHOICES,
        default='mqtt',
        verbose_name='Protocolo'
    )
    username = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Usuario',
        help_text='Usuario para autenticación en el broker'
    )
    password = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name='Contraseña',
        help_text='Contraseña para autenticación (se recomienda encriptar)'
    )
    keepalive = models.IntegerField(
        default=60,
        verbose_name='Keep Alive (segundos)',
        validators=[MinValueValidator(10), MaxValueValidator(3600)],
        help_text='Intervalo de keep-alive en segundos'
    )
    clean_session = models.BooleanField(
        default=True,
        verbose_name='Sesión Limpia',
        help_text='Si es True, el broker no guardará el estado de la sesión'
    )
    use_tls = models.BooleanField(
        default=False,
        verbose_name='Usar TLS',
        help_text='Habilitar conexión segura con TLS/SSL'
    )
    ca_cert = models.TextField(
        blank=True,
        null=True,
        verbose_name='Certificado CA',
        help_text='Certificado de la autoridad certificadora (PEM format)'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activo',
        db_index=True,
        help_text='Indica si esta configuración está activa'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Fecha de Actualización')
    
    class Meta:
        verbose_name = 'Configuración de Broker'
        verbose_name_plural = 'Configuraciones de Brokers'
        ordering = ['-is_active', 'nombre']
        db_table = 'mqtt_broker_config'
        indexes = [
            models.Index(fields=['is_active'], name='idx_broker_active'),
        ]
    
    def __str__(self):
        return f"{self.nombre} ({self.host}:{self.port})"


class MQTTCredential(models.Model):
    """
    Credenciales MQTT por dispositivo
    """
    dispositivo = models.OneToOneField(
        'devices.Dispositivo',
        on_delete=models.CASCADE,
        related_name='mqtt_credential',
        verbose_name='Dispositivo'
    )
    client_id = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Client ID',
        db_index=True,
        help_text='Identificador único del cliente MQTT'
    )
    username = models.CharField(
        max_length=100,
        verbose_name='Usuario MQTT',
        help_text='Usuario para autenticación MQTT del dispositivo'
    )
    password = models.CharField(
        max_length=255,
        verbose_name='Contraseña MQTT',
        help_text='Contraseña para autenticación MQTT (encriptada)'
    )
    use_device_cert = models.BooleanField(
        default=False,
        verbose_name='Usar Certificado de Dispositivo',
        help_text='Indica si el dispositivo usa certificado para autenticación'
    )
    client_cert = models.TextField(
        blank=True,
        null=True,
        verbose_name='Certificado del Cliente',
        help_text='Certificado del dispositivo (PEM format)'
    )
    client_key = models.TextField(
        blank=True,
        null=True,
        verbose_name='Clave Privada del Cliente',
        help_text='Clave privada del certificado (PEM format)'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activo',
        db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Fecha de Actualización')
    
    class Meta:
        verbose_name = 'Credencial MQTT'
        verbose_name_plural = 'Credenciales MQTT'
        ordering = ['-created_at']
        db_table = 'mqtt_credentials'
        indexes = [
            models.Index(fields=['client_id'], name='idx_mqtt_cred_client'),
            models.Index(fields=['is_active'], name='idx_mqtt_cred_active'),
        ]
    
    def __str__(self):
        return f"Credencial MQTT: {self.dispositivo.nombre} ({self.client_id})"


class MQTTTopic(models.Model):
    """
    Topics MQTT para publicación y suscripción
    """
    TIPO_CHOICES = [
        ('publish', 'Publicación'),
        ('subscribe', 'Suscripción'),
        ('both', 'Ambos'),
    ]
    
    nombre = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Nombre',
        help_text='Nombre descriptivo del topic'
    )
    topic_pattern = models.CharField(
        max_length=255,
        verbose_name='Patrón del Topic',
        help_text='Patrón del topic MQTT. Ej: sensors/{device_id}/{sensor_type}'
    )
    tipo = models.CharField(
        max_length=10,
        choices=TIPO_CHOICES,
        default='both',
        verbose_name='Tipo de Topic'
    )
    qos = models.IntegerField(
        default=1,
        verbose_name='QoS',
        choices=[(0, 'At most once (0)'), (1, 'At least once (1)'), (2, 'Exactly once (2)')],
        help_text='Quality of Service por defecto'
    )
    retain = models.BooleanField(
        default=False,
        verbose_name='Retener Mensaje',
        help_text='El broker retendrá el último mensaje publicado'
    )
    descripcion = models.TextField(
        blank=True,
        verbose_name='Descripción',
        help_text='Descripción del propósito del topic'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Fecha de Actualización')
    
    class Meta:
        verbose_name = 'Topic MQTT'
        verbose_name_plural = 'Topics MQTT'
        ordering = ['nombre']
        db_table = 'mqtt_topics'
        indexes = [
            models.Index(fields=['tipo'], name='idx_mqtt_topic_tipo'),
        ]
    
    def __str__(self):
        return f"{self.nombre} ({self.topic_pattern})"


class DeviceMQTTConfig(models.Model):
    """
    Configuración MQTT específica por dispositivo
    """
    CONNECTION_STATUS_CHOICES = [
        ('connected', 'Conectado'),
        ('disconnected', 'Desconectado'),
        ('error', 'Error'),
    ]
    
    dispositivo = models.OneToOneField(
        'devices.Dispositivo',
        on_delete=models.CASCADE,
        related_name='mqtt_config',
        verbose_name='Dispositivo'
    )
    broker = models.ForeignKey(
        BrokerConfig,
        on_delete=models.CASCADE,
        related_name='device_configs',
        verbose_name='Broker',
        help_text='Broker MQTT al que se conecta el dispositivo'
    )
    publish_topic = models.ForeignKey(
        MQTTTopic,
        on_delete=models.SET_NULL,
        null=True,
        related_name='publishing_devices',
        verbose_name='Topic de Publicación',
        help_text='Topic principal para publicar datos'
    )
    subscribe_topics = models.ManyToManyField(
        MQTTTopic,
        related_name='subscribing_devices',
        blank=True,
        verbose_name='Topics de Suscripción',
        help_text='Topics a los que el dispositivo está suscrito'
    )
    publish_interval = models.IntegerField(
        default=60,
        verbose_name='Intervalo de Publicación (segundos)',
        validators=[MinValueValidator(1), MaxValueValidator(86400)],
        help_text='Intervalo en segundos entre publicaciones'
    )
    qos = models.IntegerField(
        default=1,
        verbose_name='QoS',
        choices=[(0, 'At most once (0)'), (1, 'At least once (1)'), (2, 'Exactly once (2)')],
        help_text='Quality of Service para este dispositivo'
    )
    retain = models.BooleanField(
        default=False,
        verbose_name='Retener Mensajes',
        help_text='Los mensajes del dispositivo serán retenidos por el broker'
    )
    auto_reconnect = models.BooleanField(
        default=True,
        verbose_name='Auto Reconexión',
        help_text='Reconectar automáticamente en caso de desconexión'
    )
    last_connection = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Última Conexión',
        db_index=True,
        help_text='Fecha y hora de la última conexión exitosa'
    )
    connection_status = models.CharField(
        max_length=20,
        choices=CONNECTION_STATUS_CHOICES,
        default='disconnected',
        verbose_name='Estado de Conexión',
        db_index=True
    )
    metadata_json = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Metadata JSON',
        help_text='Información adicional de configuración'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activo',
        db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Fecha de Actualización')
    
    class Meta:
        verbose_name = 'Configuración MQTT de Dispositivo'
        verbose_name_plural = 'Configuraciones MQTT de Dispositivos'
        ordering = ['-last_connection']
        db_table = 'mqtt_device_config'
        indexes = [
            models.Index(fields=['connection_status'], name='idx_mqtt_dev_status'),
            models.Index(fields=['last_connection'], name='idx_mqtt_dev_last_conn'),
            models.Index(fields=['is_active'], name='idx_mqtt_dev_active'),
        ]
    
    def __str__(self):
        return f"Config MQTT: {self.dispositivo.nombre}"
