"""
Configuracion del Django Admin para la app Devices
"""

from django.contrib import admin
from .models import Dispositivo, DispositivoSensor


@admin.register(Dispositivo)
class DispositivoAdmin(admin.ModelAdmin):
    """
    Admin para el modelo Dispositivo
    """
    list_display = ['nombre', 'tipo', 'identificador_unico', 'ubicacion', 'estado', 'mqtt_enabled', 'connection_status', 'operador_asignado', 'created_at']
    list_filter = ['tipo', 'estado', 'mqtt_enabled', 'connection_status', 'created_at']
    search_fields = ['nombre', 'identificador_unico', 'ubicacion']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at', 'last_seen']
    
    fieldsets = (
        ('Informacion Basica', {
            'fields': ('nombre', 'tipo', 'identificador_unico', 'ubicacion', 'estado', 'descripcion')
        }),
        ('Asignacion', {
            'fields': ('operador_asignado',)
        }),
        ('Configuracion MQTT', {
            'fields': ('mqtt_enabled', 'mqtt_client_id', 'connection_status', 'last_seen'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(DispositivoSensor)
class DispositivoSensorAdmin(admin.ModelAdmin):
    """
    Admin para el modelo DispositivoSensor
    """
    list_display = ['dispositivo', 'sensor', 'activo', 'fecha_asignacion']
    list_filter = ['activo', 'fecha_asignacion']
    search_fields = ['dispositivo__nombre', 'sensor__nombre']
    ordering = ['-fecha_asignacion']
    readonly_fields = ['fecha_asignacion']
