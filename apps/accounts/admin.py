"""
Configuracion del Django Admin para la app Accounts
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Rol, Permiso


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Admin para el modelo CustomUser
    """
    list_display = ['username', 'email', 'tipo_usuario', 'rol', 'is_active', 'is_staff', 'created_at']
    list_filter = ['tipo_usuario', 'rol', 'is_active', 'is_staff', 'is_superuser']
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering = ['-created_at']
    
    fieldsets = UserAdmin.fieldsets + (
        ('Informacion Adicional', {
            'fields': ('tipo_usuario', 'rol', 'created_at', 'updated_at')
        }),
    )
    readonly_fields = ['created_at', 'updated_at', 'last_login']


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
