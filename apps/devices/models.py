"""
Modelos de la app Devices - Gestión de Dispositivos IoT
"""

from django.db import models
from django.conf import settings


class Dispositivo(models.Model):
    """
    Modelo de Dispositivos IoT
    """
    TIPO_DISPOSITIVO_CHOICES = [
        ('raspberry_pi', 'Raspberry Pi'),
        ('esp32', 'ESP32'),
        ('arduino', 'Arduino'),
        ('esp8266', 'ESP8266'),
        ('stm32', 'STM32'),
        ('otro', 'Otro'),
    ]
    
    ESTADO_CHOICES = [
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
        ('mantenimiento', 'Mantenimiento'),
        ('desconectado', 'Desconectado'),
    ]
    
    CONNECTION_STATUS_CHOICES = [
        ('online', 'En Línea'),
        ('offline', 'Fuera de Línea'),
        ('error', 'Error'),
    ]
    
    nombre = models.CharField(max_length=200, verbose_name='Nombre')
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_DISPOSITIVO_CHOICES,
        verbose_name='Tipo de Dispositivo'
    )
    identificador_unico = models.CharField(
        max_length=100,
        unique=True,
        verbose_name='Identificador Único',
        db_index=True
    )
    ubicacion = models.CharField(max_length=300, verbose_name='Ubicación')
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='inactivo',
        verbose_name='Estado',
        db_index=True
    )
    descripcion = models.TextField(blank=True, verbose_name='Descripción')
    
    # Campos MQTT
    mqtt_enabled = models.BooleanField(
        default=False,
        verbose_name='MQTT Habilitado',
        db_index=True,
        help_text='Indica si el dispositivo tiene MQTT habilitado'
    )
    mqtt_client_id = models.CharField(
        max_length=100,
        unique=True,
        null=True,
        blank=True,
        verbose_name='Client ID MQTT',
        db_index=True,
        help_text='Identificador único del cliente MQTT'
    )
    last_seen = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Última Conexión',
        help_text='Última vez que el dispositivo se conectó'
    )
    connection_status = models.CharField(
        max_length=20,
        choices=CONNECTION_STATUS_CHOICES,
        default='offline',
        verbose_name='Estado de Conexión',
        db_index=True
    )
    
    # Sensores asociados (relación many-to-many a través de DispositivoSensor)
    sensores = models.ManyToManyField(
        'sensors.Sensor',
        through='DispositivoSensor',
        related_name='dispositivos',
        verbose_name='Sensores'
    )
    
    # Operador asignado al dispositivo
    operador_asignado = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='dispositivos_asignados',
        verbose_name='Operador Asignado',
        db_index=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Fecha de Actualización')
    
    class Meta:
        verbose_name = 'Dispositivo'
        verbose_name_plural = 'Dispositivos'
        ordering = ['-created_at']
        db_table = 'dispositivos'
        indexes = [
            models.Index(fields=['estado'], name='idx_dispositivo_estado'),
            models.Index(fields=['operador_asignado'], name='idx_dispositivo_operador'),
            models.Index(fields=['mqtt_enabled'], name='idx_dispositivo_mqtt'),
            models.Index(fields=['connection_status'], name='idx_dispositivo_conn_status'),
            models.Index(fields=['-created_at'], name='idx_dispositivo_created'),
        ]
    
    def __str__(self):
        return f"{self.nombre} ({self.identificador_unico})"


class DispositivoSensor(models.Model):
    """
    Modelo intermedio para la relación many-to-many entre Dispositivo y Sensor
    """
    dispositivo = models.ForeignKey(
        Dispositivo,
        on_delete=models.CASCADE,
        verbose_name='Dispositivo'
    )
    sensor = models.ForeignKey(
        'sensors.Sensor',
        on_delete=models.CASCADE,
        verbose_name='Sensor'
    )
    configuracion_json = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Configuración JSON',
        help_text='Configuración específica de este sensor en este dispositivo'
    )
    fecha_asignacion = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha de Asignación'
    )
    activo = models.BooleanField(default=True, verbose_name='Activo')
    
    class Meta:
        verbose_name = 'Dispositivo-Sensor'
        verbose_name_plural = 'Dispositivos-Sensores'
        unique_together = ['dispositivo', 'sensor']
        ordering = ['-fecha_asignacion']
        db_table = 'dispositivos_sensores'
        indexes = [
            models.Index(fields=['dispositivo', 'sensor'], name='idx_disp_sensor'),
            models.Index(fields=['activo'], name='idx_disp_sensor_activo'),
        ]
    
    def __str__(self):
        return f"{self.dispositivo.nombre} - {self.sensor.nombre}"
