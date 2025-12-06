"""
Configuracion del Django Admin para la app MQTT
"""

from django.contrib import admin
from .models import BrokerConfig, MQTTCredential, MQTTTopic, DeviceMQTTConfig, EMQXUser, EMQXACL


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


class EMQXACLInline(admin.TabularInline):
    """
    Inline para mostrar reglas ACL dentro del admin de EMQXUser
    """
    model = EMQXACL
    extra = 1
    fields = ['permission', 'action', 'topic', 'qos', 'retain']


@admin.register(EMQXUser)
class EMQXUserAdmin(admin.ModelAdmin):
    """
    Admin para el modelo EMQXUser (Autenticación EMQX)
    """
    list_display = ['username', 'is_superuser', 'dispositivo', 'created']
    list_filter = ['is_superuser', 'created']
    search_fields = ['username', 'dispositivo__nombre']
    ordering = ['-created']
    readonly_fields = ['created', 'password_hash', 'salt']
    inlines = [EMQXACLInline]
    
    fieldsets = (
        ('Usuario MQTT', {
            'fields': ('username', 'is_superuser', 'dispositivo')
        }),
        ('Seguridad (Solo Lectura)', {
            'fields': ('password_hash', 'salt'),
            'classes': ('collapse',),
            'description': 'Los hashes se generan automáticamente. Use la API o métodos del modelo para cambiar contraseñas.'
        }),
        ('Metadata', {
            'fields': ('created',),
            'classes': ('collapse',)
        }),
    )
    
    def get_readonly_fields(self, request, obj=None):
        """
        Hacer password_hash y salt siempre readonly
        """
        if obj:  # Editing
            return self.readonly_fields + ('username',)
        return self.readonly_fields


@admin.register(EMQXACL)
class EMQXACLAdmin(admin.ModelAdmin):
    """
    Admin para el modelo EMQXACL (Autorización EMQX)
    """
    list_display = ['username', 'permission', 'action', 'topic', 'qos', 'retain', 'created_at']
    list_filter = ['permission', 'action', 'qos', 'retain', 'created_at']
    search_fields = ['username', 'topic']
    ordering = ['username', 'topic']
    readonly_fields = ['created_at']
    autocomplete_fields = ['emqx_user']
    
    fieldsets = (
        ('Regla ACL', {
            'fields': ('username', 'emqx_user')
        }),
        ('Permisos', {
            'fields': ('permission', 'action', 'topic')
        }),
        ('Opciones MQTT', {
            'fields': ('qos', 'retain'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    def get_form(self, request, obj=None, **kwargs):
        """
        Personalizar el formulario para ayudar con la selección de username
        """
        form = super().get_form(request, obj, **kwargs)
        if not obj:  # Nuevo objeto
            form.base_fields['username'].help_text = (
                'Debe coincidir con un usuario EMQX existente. '
                'Seleccione el usuario EMQX abajo para autocompletar.'
            )
        return form
