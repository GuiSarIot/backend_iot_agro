"""
Configuracion del Django Admin para la app Readings
"""

from django.contrib import admin
from .models import Lectura


@admin.register(Lectura)
class LecturaAdmin(admin.ModelAdmin):
    """
    Admin para el modelo Lectura
    """
    list_display = ['dispositivo', 'sensor', 'valor', 'timestamp', 'mqtt_message_id', 'mqtt_qos']
    list_filter = ['dispositivo', 'sensor', 'timestamp', 'mqtt_qos']
    search_fields = ['dispositivo__nombre', 'sensor__nombre', 'mqtt_message_id']
    ordering = ['-timestamp']
    readonly_fields = ['timestamp']
    
    # Limitar resultados para mejor rendimiento
    list_per_page = 50
    
    fieldsets = (
        ('Lectura', {
            'fields': ('dispositivo', 'sensor', 'valor', 'timestamp')
        }),
        ('Metadata', {
            'fields': ('metadata_json',),
            'classes': ('collapse',)
        }),
        ('Informacion MQTT', {
            'fields': ('mqtt_message_id', 'mqtt_qos', 'mqtt_retained'),
            'classes': ('collapse',)
        }),
    )
