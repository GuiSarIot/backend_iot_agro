"""
Configuracion del Django Admin para la app MQTT
"""

from django.contrib import admin
from .models import BrokerConfig, MQTTCredential, MQTTTopic, DeviceMQTTConfig


@admin.register(BrokerConfig)
class BrokerConfigAdmin(admin.ModelAdmin):
    """
    Admin para el modelo BrokerConfig
    """
    list_display = ['nombre', 'host', 'port', 'protocol', 'use_tls', 'is_active', 'created_at']
    list_filter = ['protocol', 'use_tls', 'is_active', 'created_at']
    search_fields = ['nombre', 'host']
    ordering = ['-is_active', 'nombre']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Configuracion Basica', {
            'fields': ('nombre', 'host', 'port', 'protocol', 'is_active')
        }),
        ('Autenticacion', {
            'fields': ('username', 'password'),
            'classes': ('collapse',)
        }),
        ('Configuracion Avanzada', {
            'fields': ('keepalive', 'clean_session', 'use_tls', 'ca_cert'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(MQTTCredential)
class MQTTCredentialAdmin(admin.ModelAdmin):
    """
    Admin para el modelo MQTTCredential
    """
    list_display = ['dispositivo', 'client_id', 'username', 'use_device_cert', 'is_active', 'created_at']
    list_filter = ['use_device_cert', 'is_active', 'created_at']
    search_fields = ['client_id', 'username', 'dispositivo__nombre']
    ordering = ['-created_at']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Dispositivo', {
            'fields': ('dispositivo', 'is_active')
        }),
        ('Credenciales MQTT', {
            'fields': ('client_id', 'username', 'password')
        }),
        ('Certificados', {
            'fields': ('use_device_cert', 'client_cert', 'client_key'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(MQTTTopic)
class MQTTTopicAdmin(admin.ModelAdmin):
    """
    Admin para el modelo MQTTTopic
    """
    list_display = ['nombre', 'topic_pattern', 'tipo', 'qos', 'retain', 'created_at']
    list_filter = ['tipo', 'qos', 'retain', 'created_at']
    search_fields = ['nombre', 'topic_pattern', 'descripcion']
    ordering = ['nombre']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Topic MQTT', {
            'fields': ('nombre', 'topic_pattern', 'tipo', 'descripcion')
        }),
        ('Configuracion', {
            'fields': ('qos', 'retain')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(DeviceMQTTConfig)
class DeviceMQTTConfigAdmin(admin.ModelAdmin):
    """
    Admin para el modelo DeviceMQTTConfig
    """
    list_display = ['dispositivo', 'broker', 'connection_status', 'last_connection', 'is_active', 'created_at']
    list_filter = ['connection_status', 'is_active', 'created_at']
    search_fields = ['dispositivo__nombre', 'broker__nombre']
    ordering = ['-last_connection']
    readonly_fields = ['last_connection', 'created_at', 'updated_at']
    filter_horizontal = ['subscribe_topics']
    
    fieldsets = (
        ('Dispositivo y Broker', {
            'fields': ('dispositivo', 'broker', 'is_active')
        }),
        ('Topics', {
            'fields': ('publish_topic', 'subscribe_topics')
        }),
        ('Configuracion', {
            'fields': ('publish_interval', 'qos', 'retain', 'auto_reconnect')
        }),
        ('Estado', {
            'fields': ('connection_status', 'last_connection')
        }),
        ('Metadata', {
            'fields': ('metadata_json', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
