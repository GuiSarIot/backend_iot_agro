"""
Configuracion del Django Admin para la app Sensors
"""

from django.contrib import admin
from .models import Sensor


@admin.register(Sensor)
class SensorAdmin(admin.ModelAdmin):
    """
    Admin para el modelo Sensor
    """
    list_display = ['nombre', 'tipo', 'unidad_medida', 'rango_min', 'rango_max', 'estado', 'mqtt_topic_suffix', 'created_by', 'created_at']
    list_filter = ['tipo', 'estado', 'created_at']
    search_fields = ['nombre', 'descripcion']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Informacion Basica', {
            'fields': ('nombre', 'tipo', 'estado', 'descripcion')
        }),
        ('Especificaciones', {
            'fields': ('unidad_medida', 'rango_min', 'rango_max')
        }),
        ('Configuracion MQTT', {
            'fields': ('mqtt_topic_suffix', 'publish_interval'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
