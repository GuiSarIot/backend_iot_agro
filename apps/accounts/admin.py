"""
Configuracion del Django Admin para la app Accounts
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from .models import CustomUser, Rol, Permiso, AuditLog, AccessLog


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Admin para el modelo CustomUser
    """
    list_display = [
        'username', 'email', 'tipo_usuario', 'rol', 
        'is_active', 'is_staff', 'telegram_status_badge', 'email_status_badge', 'created_at'
    ]
    list_filter = [
        'tipo_usuario', 'rol', 'is_active', 'is_staff', 'is_superuser',
        'telegram_verified', 'telegram_notifications_enabled',
        'email_verified', 'email_notifications_enabled'
    ]
    search_fields = ['username', 'email', 'first_name', 'last_name', 'telegram_username']
    ordering = ['-created_at']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Informacion Adicional', {
            'fields': ('tipo_usuario', 'rol', 'created_at', 'updated_at')
        }),
        ('Integración Telegram', {
            'fields': (
                'telegram_chat_id', 'telegram_username', 
                'telegram_verified', 'telegram_notifications_enabled',
                'telegram_verification_code', 'telegram_verification_expires'
            ),
            'classes': ('collapse',)
        }),
        ('Integración Email', {
            'fields': (
                'email_notifications_enabled', 'email_verified',
                'email_verification_token', 'email_verification_sent_at'
            ),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = [
        'created_at', 'updated_at', 'last_login',
        'telegram_verification_code', 'telegram_verification_expires',
        'email_verification_token', 'email_verification_sent_at'
    ]
    
    def telegram_status_badge(self, obj):
        """Muestra el estado de Telegram con badge"""
        if obj.can_receive_telegram_notifications:
            return format_html(
                '<span style="background-color: green; color: white; padding: 3px 8px; border-radius: 3px;">✓ Activo</span>'
            )
        elif obj.telegram_verified:
            return format_html(
                '<span style="background-color: orange; color: white; padding: 3px 8px; border-radius: 3px;">⚠ Notif. Off</span>'
            )
        elif obj.telegram_chat_id:
            return format_html(
                '<span style="background-color: gray; color: white; padding: 3px 8px; border-radius: 3px;">◐ Vinculado</span>'
            )
        else:
            return format_html(
                '<span style="background-color: lightgray; color: black; padding: 3px 8px; border-radius: 3px;">✗ No vinculado</span>'
            )
    telegram_status_badge.short_description = 'Telegram'
    
    def email_status_badge(self, obj):
        """Muestra el estado de Email con badge"""
        if obj.can_receive_email_notifications:
            return format_html(
                '<span style="background-color: green; color: white; padding: 3px 8px; border-radius: 3px;">✓ Verificado</span>'
            )
        elif obj.email_verified:
            return format_html(
                '<span style="background-color: orange; color: white; padding: 3px 8px; border-radius: 3px;">⚠ Notif. Off</span>'
            )
        elif obj.email:
            return format_html(
                '<span style="background-color: gray; color: white; padding: 3px 8px; border-radius: 3px;">◐ Sin verificar</span>'
            )
        else:
            return format_html(
                '<span style="background-color: lightgray; color: black; padding: 3px 8px; border-radius: 3px;">✗ Sin email</span>'
            )
    email_status_badge.short_description = 'Email'


@admin.register(Permiso)
class PermisoAdmin(admin.ModelAdmin):
    """
    Admin para el modelo Permiso
    """
    list_display = ['nombre', 'codigo', 'descripcion', 'created_at']
    search_fields = ['nombre', 'codigo', 'descripcion']
    ordering = ['nombre']
    readonly_fields = ['created_at']


@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    """
    Admin para el modelo Rol
    """
    list_display = ['nombre', 'descripcion', 'created_at']
    filter_horizontal = ['permisos']
    search_fields = ['nombre', 'descripcion']
    ordering = ['nombre']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """
    Admin para registros de auditoría (solo lectura)
    """
    list_display = ['timestamp', 'username', 'action_badge', 'model_name', 'object_repr', 'ip_address']
    list_filter = ['action', 'model_name', 'timestamp']
    search_fields = ['username', 'model_name', 'object_repr', 'ip_address']
    ordering = ['-timestamp']
    readonly_fields = [
        'user', 'username', 'model_name', 'object_id', 'object_repr',
        'action', 'changes', 'ip_address', 'user_agent', 'timestamp'
    ]
    date_hierarchy = 'timestamp'
    
    def action_badge(self, obj):
        """Colorea las acciones"""
        colors = {
            'CREATE': 'green',
            'UPDATE': 'blue',
            'DELETE': 'red',
        }
        color = colors.get(obj.action, 'gray')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_action_display()
        )
    action_badge.short_description = 'Acción'
    
    def has_add_permission(self, request):
        """No permitir agregar manualmente"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Solo superusuarios pueden eliminar logs"""
        return request.user.is_superuser


@admin.register(AccessLog)
class AccessLogAdmin(admin.ModelAdmin):
    """
    Admin para registros de acceso (solo lectura)
    """
    list_display = [
        'timestamp', 'username', 'module', 'method', 'endpoint_short',
        'status_badge', 'response_time_badge', 'ip_address'
    ]
    list_filter = ['module', 'method', 'status_code', 'timestamp']
    search_fields = ['username', 'endpoint', 'ip_address']
    ordering = ['-timestamp']
    readonly_fields = [
        'user', 'username', 'module', 'endpoint', 'method', 'status_code',
        'ip_address', 'user_agent', 'response_time_ms', 'query_params',
        'metadata', 'timestamp'
    ]
    date_hierarchy = 'timestamp'
    
    def endpoint_short(self, obj):
        """Muestra endpoint acortado"""
        endpoint = obj.endpoint
        if len(endpoint) > 50:
            return endpoint[:47] + '...'
        return endpoint
    endpoint_short.short_description = 'Endpoint'
    
    def status_badge(self, obj):
        """Colorea el status code"""
        if obj.status_code < 300:
            color = 'green'
        elif obj.status_code < 400:
            color = 'blue'
        elif obj.status_code < 500:
            color = 'orange'
        else:
            color = 'red'
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px; font-weight: bold;">{}</span>',
            color,
            obj.status_code
        )
    status_badge.short_description = 'Status'
    
    def response_time_badge(self, obj):
        """Muestra tiempo de respuesta con color"""
        if not obj.response_time_ms:
            return '-'
        
        if obj.response_time_ms < 500:
            color = 'green'
        elif obj.response_time_ms < 2000:
            color = 'orange'
        else:
            color = 'red'
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{} ms</span>',
            color,
            obj.response_time_ms
        )
    response_time_badge.short_description = 'Tiempo'
    
    def has_add_permission(self, request):
        """No permitir agregar manualmente"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Solo superusuarios pueden eliminar logs"""
        return request.user.is_superuser
