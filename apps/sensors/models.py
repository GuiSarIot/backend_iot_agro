"""
Modelos de la app Sensors - Gestión de Sensores IoT
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.conf import settings


class Sensor(models.Model):
    """
    Modelo de Sensores IoT
    """
    TIPO_SENSOR_CHOICES = [
        ('temperatura', 'Temperatura'),
        ('humedad', 'Humedad'),
        ('presion', 'Presión'),
        ('luz', 'Luz'),
        ('movimiento', 'Movimiento'),
        ('gas', 'Gas'),
        ('sonido', 'Sonido'),
        ('distancia', 'Distancia'),
        ('acelerometro', 'Acelerómetro'),
        ('giroscopio', 'Giroscopio'),
        ('otro', 'Otro'),
    ]
    
    ESTADO_CHOICES = [
        ('activo', 'Activo'),
        ('inactivo', 'Inactivo'),
        ('mantenimiento', 'Mantenimiento'),
    ]
    
    nombre = models.CharField(max_length=200, verbose_name='Nombre')
    tipo = models.CharField(
        max_length=20,
        choices=TIPO_SENSOR_CHOICES,
        verbose_name='Tipo de Sensor',
        db_index=True
    )
    unidad_medida = models.CharField(max_length=50, verbose_name='Unidad de Medida')
    rango_min = models.FloatField(
        validators=[MinValueValidator(-1000000)],
        verbose_name='Rango Mínimo'
    )
    rango_max = models.FloatField(
        validators=[MaxValueValidator(1000000)],
        verbose_name='Rango Máximo'
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_CHOICES,
        default='activo',
        verbose_name='Estado',
        db_index=True
    )
    descripcion = models.TextField(blank=True, verbose_name='Descripción')
    
    # Campos MQTT
    mqtt_topic_suffix = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name='Sufijo de Topic MQTT',
        help_text='Ejemplo: temperature, humidity. Se usará en el topic MQTT.'
    )
    publish_interval = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='Intervalo de Publicación (segundos)',
        help_text='Intervalo recomendado para publicar lecturas de este sensor',
        validators=[MinValueValidator(1), MaxValueValidator(86400)]
    )
    
    # Relación con el usuario que lo creó
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='sensores_creados',
        verbose_name='Creado por',
        db_index=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Fecha de Actualización')
    
    class Meta:
        verbose_name = 'Sensor'
        verbose_name_plural = 'Sensores'
        ordering = ['-created_at']
        db_table = 'sensores'
        indexes = [
            models.Index(fields=['tipo'], name='idx_sensor_tipo'),
            models.Index(fields=['estado'], name='idx_sensor_estado'),
            models.Index(fields=['created_by'], name='idx_sensor_created_by'),
            models.Index(fields=['-created_at'], name='idx_sensor_created_at'),
        ]
    
    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_display()})"
    
    def clean(self):
        from django.core.exceptions import ValidationError
        if self.rango_min >= self.rango_max:
            raise ValidationError('El rango mínimo debe ser menor que el rango máximo')
