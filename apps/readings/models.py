"""
Modelos de la app Readings - Gestión de Lecturas de Sensores
"""

from django.db import models


class Lectura(models.Model):
    """
    Modelo de Lecturas de sensores
    """
    dispositivo = models.ForeignKey(
        'devices.Dispositivo',
        on_delete=models.CASCADE,
        related_name='lecturas',
        verbose_name='Dispositivo'
    )
    sensor = models.ForeignKey(
        'sensors.Sensor',
        on_delete=models.CASCADE,
        related_name='lecturas',
        verbose_name='Sensor'
    )
    valor = models.FloatField(verbose_name='Valor')
    timestamp = models.DateTimeField(
        auto_now_add=True, 
        verbose_name='Timestamp',
        db_index=True
    )
    metadata_json = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Metadata JSON',
        help_text='Información adicional sobre la lectura'
    )
    
    # Campos MQTT
    mqtt_message_id = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        verbose_name='ID Mensaje MQTT',
        help_text='Identificador del mensaje MQTT que generó esta lectura'
    )
    mqtt_qos = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='QoS MQTT',
        choices=[(0, 'At most once (0)'), (1, 'At least once (1)'), (2, 'Exactly once (2)')],
        help_text='Quality of Service del mensaje MQTT'
    )
    mqtt_retained = models.BooleanField(
        default=False,
        verbose_name='Mensaje Retenido',
        help_text='Indica si el mensaje MQTT fue retenido en el broker'
    )
    
    class Meta:
        verbose_name = 'Lectura'
        verbose_name_plural = 'Lecturas'
        ordering = ['-timestamp']
        db_table = 'lecturas'
        indexes = [
            models.Index(fields=['-timestamp'], name='idx_lectura_timestamp'),
            models.Index(fields=['dispositivo', '-timestamp'], name='idx_lectura_disp_ts'),
            models.Index(fields=['sensor', '-timestamp'], name='idx_lectura_sensor_ts'),
            models.Index(fields=['mqtt_message_id'], name='idx_lectura_mqtt_msg'),
        ]
    
    def __str__(self):
        return f"{self.sensor.nombre}: {self.valor} ({self.timestamp})"
    
    def clean(self):
        from django.core.exceptions import ValidationError
        # Validar que el valor esté dentro del rango del sensor
        if self.valor < self.sensor.rango_min or self.valor > self.sensor.rango_max:
            raise ValidationError(
                f'El valor {self.valor} está fuera del rango permitido '
                f'({self.sensor.rango_min} - {self.sensor.rango_max})'
            )
