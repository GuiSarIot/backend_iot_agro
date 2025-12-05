"""
Modelos de la app Accounts - Gestión de Usuarios, Roles y Permisos
"""

from django.db import models
from django.contrib.auth.models import AbstractUser


class Permiso(models.Model):
    """
    Modelo de Permisos del sistema
    """
    nombre = models.CharField(max_length=100, unique=True, verbose_name='Nombre')
    codigo = models.CharField(
        max_length=50, 
        unique=True, 
        verbose_name='Código',
        db_index=True
    )
    descripcion = models.TextField(blank=True, verbose_name='Descripción')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    
    class Meta:
        verbose_name = 'Permiso'
        verbose_name_plural = 'Permisos'
        ordering = ['nombre']
        db_table = 'permisos'
        indexes = [
            models.Index(fields=['codigo'], name='idx_permiso_codigo'),
        ]
    
    def __str__(self):
        return f"{self.nombre} ({self.codigo})"


class Rol(models.Model):
    """
    Modelo de Roles del sistema
    """
    NOMBRE_ROL_CHOICES = [
        ('superusuario', 'Superusuario'),
        ('operador', 'Operador'),
        ('solo_lectura', 'Solo Lectura'),
    ]
    
    nombre = models.CharField(
        max_length=50,
        choices=NOMBRE_ROL_CHOICES,
        unique=True,
        verbose_name='Nombre',
        db_index=True
    )
    descripcion = models.TextField(blank=True, verbose_name='Descripción')
    permisos = models.ManyToManyField(
        Permiso,
        related_name='roles',
        blank=True,
        verbose_name='Permisos'
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Fecha de Actualización')
    
    class Meta:
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'
        ordering = ['nombre']
        db_table = 'roles'
        indexes = [
            models.Index(fields=['nombre'], name='idx_rol_nombre'),
        ]
    
    def __str__(self):
        return self.get_nombre_display()


class CustomUser(AbstractUser):
    """
    Modelo de usuario personalizado que extiende AbstractUser
    """
    TIPO_USUARIO_CHOICES = [
        ('interno', 'Interno'),
        ('externo', 'Externo'),
    ]
    
    tipo_usuario = models.CharField(
        max_length=10,
        choices=TIPO_USUARIO_CHOICES,
        default='externo',
        verbose_name='Tipo de Usuario',
        db_index=True
    )
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Fecha de Actualización')
    
    # Relación con Rol
    rol = models.ForeignKey(
        Rol,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='usuarios',
        verbose_name='Rol',
        db_index=True
    )
    
    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'
        ordering = ['-created_at']
        db_table = 'users'
        indexes = [
            models.Index(fields=['tipo_usuario'], name='idx_user_tipo'),
            models.Index(fields=['rol'], name='idx_user_rol'),
            models.Index(fields=['-created_at'], name='idx_user_created'),
        ]
    
    def __str__(self):
        return f"{self.username} ({self.get_tipo_usuario_display()})"
    
    def has_permission(self, codigo_permiso):
        """
        Verifica si el usuario tiene un permiso específico
        """
        if self.is_superuser:
            return True
        if self.rol:
            return self.rol.permisos.filter(codigo=codigo_permiso).exists()
        return False
