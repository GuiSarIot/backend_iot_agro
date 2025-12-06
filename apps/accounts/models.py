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
    
    # Integración Telegram
    telegram_chat_id = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        unique=True,
        verbose_name='Telegram Chat ID',
        db_index=True,
        help_text='ID de chat de Telegram para notificaciones'
    )
    telegram_username = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name='Usuario de Telegram',
        help_text='Username de Telegram (@username)'
    )
    telegram_notifications_enabled = models.BooleanField(
        default=False,
        verbose_name='Notificaciones Telegram Habilitadas',
        help_text='Recibir notificaciones via Telegram'
    )
    telegram_verified = models.BooleanField(
        default=False,
        verbose_name='Telegram Verificado',
        help_text='Indica si el usuario verificó su cuenta de Telegram'
    )
    telegram_verification_code = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        verbose_name='Código de Verificación Telegram',
        help_text='Código temporal para verificar cuenta'
    )
    telegram_verification_expires = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Expiración de Verificación',
        help_text='Fecha de expiración del código de verificación'
    )
    
    # Integración Email
    email_notifications_enabled = models.BooleanField(
        default=True,
        verbose_name='Notificaciones Email Habilitadas',
        help_text='Recibir notificaciones via correo electrónico'
    )
    email_verified = models.BooleanField(
        default=False,
        verbose_name='Email Verificado',
        help_text='Indica si el usuario verificó su correo electrónico'
    )
    email_verification_token = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        unique=True,
        verbose_name='Token de Verificación Email',
        help_text='Token para verificar correo electrónico'
    )
    email_verification_sent_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name='Fecha de Envío de Verificación',
        help_text='Última vez que se envió email de verificación'
    )
    
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
            models.Index(fields=['telegram_chat_id'], name='idx_user_telegram_chat'),
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
    
    def generate_telegram_verification_code(self):
        """
        Genera un código de verificación para vincular Telegram
        """
        import secrets
        from django.utils import timezone
        from datetime import timedelta
        
        self.telegram_verification_code = secrets.token_hex(4).upper()  # 8 caracteres
        self.telegram_verification_expires = timezone.now() + timedelta(minutes=15)
        self.save(update_fields=['telegram_verification_code', 'telegram_verification_expires'])
        return self.telegram_verification_code
    
    def verify_telegram_code(self, code):
        """
        Verifica el código de Telegram y vincula la cuenta
        """
        from django.utils import timezone
        
        if not self.telegram_verification_code:
            return False, "No hay código de verificación generado"
        
        if self.telegram_verification_expires < timezone.now():
            return False, "El código ha expirado"
        
        if self.telegram_verification_code.upper() != code.upper():
            return False, "Código incorrecto"
        
        # Verificación exitosa
        self.telegram_verified = True
        self.telegram_verification_code = None
        self.telegram_verification_expires = None
        self.save(update_fields=['telegram_verified', 'telegram_verification_code', 'telegram_verification_expires'])
        
        return True, "Telegram verificado exitosamente"
    
    @property
    def can_receive_telegram_notifications(self):
        """Indica si el usuario puede recibir notificaciones de Telegram"""
        return (
            self.telegram_chat_id and 
            self.telegram_verified and 
            self.telegram_notifications_enabled
        )
    
    @property
    def can_receive_email_notifications(self):
        """
        Verifica si el usuario puede recibir notificaciones por email
        """
        return (
            self.email_notifications_enabled and
            self.email_verified and
            self.email
        )
    
    def generate_email_verification_token(self):
        """
        Genera un token de verificación para el email
        """
        import secrets
        from django.utils import timezone
        
        self.email_verification_token = secrets.token_urlsafe(32)
        self.email_verification_sent_at = timezone.now()
        self.save(update_fields=['email_verification_token', 'email_verification_sent_at'])
        return self.email_verification_token
    
    def verify_email_token(self, token):
        """
        Verifica el token de email
        """
        from django.utils import timezone
        from datetime import timedelta
        
        if not self.email_verification_token:
            return False, "No hay token de verificación generado"
        
        # Token expira en 24 horas
        if self.email_verification_sent_at:
            expires_at = self.email_verification_sent_at + timedelta(hours=24)
            if expires_at < timezone.now():
                return False, "El token ha expirado"
        
        if self.email_verification_token != token:
            return False, "Token inválido"
        
        self.email_verified = True
        self.email_verification_token = None
        self.email_verification_sent_at = None
        self.save(update_fields=['email_verified', 'email_verification_token', 'email_verification_sent_at'])
        
        return True, "Email verificado exitosamente"


class AuditLog(models.Model):
    """
    Modelo de Auditoría para registrar cambios en modelos críticos
    Rastrea CREATE, UPDATE, DELETE de registros importantes
    """
    ACTION_CHOICES = [
        ('CREATE', 'Crear'),
        ('UPDATE', 'Actualizar'),
        ('DELETE', 'Eliminar'),
    ]
    
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='audit_logs',
        verbose_name='Usuario',
        db_index=True,
        help_text='Usuario que realizó la acción'
    )
    username = models.CharField(
        max_length=150,
        verbose_name='Nombre de Usuario',
        help_text='Guardado por si el usuario es eliminado'
    )
    model_name = models.CharField(
        max_length=100,
        verbose_name='Modelo',
        db_index=True,
        help_text='Nombre del modelo afectado (ej: Dispositivo, Sensor)'
    )
    object_id = models.IntegerField(
        verbose_name='ID del Objeto',
        db_index=True,
        help_text='ID del registro afectado'
    )
    object_repr = models.CharField(
        max_length=200,
        verbose_name='Representación del Objeto',
        help_text='String representation del objeto'
    )
    action = models.CharField(
        max_length=10,
        choices=ACTION_CHOICES,
        verbose_name='Acción',
        db_index=True
    )
    changes = models.JSONField(
        default=dict,
        verbose_name='Cambios',
        help_text='Diccionario con los cambios realizados (antes/después)'
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name='Dirección IP',
        help_text='IP desde donde se realizó la acción'
    )
    user_agent = models.TextField(
        blank=True,
        verbose_name='User Agent',
        help_text='Información del navegador/cliente'
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha y Hora',
        db_index=True
    )
    
    class Meta:
        verbose_name = 'Registro de Auditoría'
        verbose_name_plural = 'Registros de Auditoría'
        ordering = ['-timestamp']
        db_table = 'audit_logs'
        indexes = [
            models.Index(fields=['-timestamp'], name='idx_audit_timestamp'),
            models.Index(fields=['model_name', '-timestamp'], name='idx_audit_model_ts'),
            models.Index(fields=['user', '-timestamp'], name='idx_audit_user_ts'),
            models.Index(fields=['action', '-timestamp'], name='idx_audit_action_ts'),
            models.Index(fields=['model_name', 'object_id'], name='idx_audit_model_obj'),
        ]
    
    def __str__(self):
        return f"{self.username} - {self.action} {self.model_name} #{self.object_id} ({self.timestamp})"


class AccessLog(models.Model):
    """
    Modelo de Historial de Acceso a Módulos
    Registra cada acceso a endpoints/módulos del sistema
    """
    MODULE_CHOICES = [
        ('auth', 'Autenticación'),
        ('users', 'Usuarios'),
        ('roles', 'Roles'),
        ('permissions', 'Permisos'),
        ('devices', 'Dispositivos'),
        ('sensors', 'Sensores'),
        ('readings', 'Lecturas'),
        ('mqtt', 'MQTT'),
        ('emqx', 'EMQX'),
        ('admin', 'Administración'),
        ('api_docs', 'Documentación API'),
        ('other', 'Otro'),
    ]
    
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='access_logs',
        verbose_name='Usuario',
        db_index=True
    )
    username = models.CharField(
        max_length=150,
        verbose_name='Nombre de Usuario',
        help_text='Username o "anonymous" para usuarios no autenticados'
    )
    module = models.CharField(
        max_length=20,
        choices=MODULE_CHOICES,
        verbose_name='Módulo',
        db_index=True,
        help_text='Módulo o sección accedida'
    )
    endpoint = models.CharField(
        max_length=255,
        verbose_name='Endpoint',
        db_index=True,
        help_text='URL del endpoint accedido'
    )
    method = models.CharField(
        max_length=10,
        verbose_name='Método HTTP',
        help_text='GET, POST, PUT, PATCH, DELETE'
    )
    status_code = models.IntegerField(
        verbose_name='Código de Estado',
        db_index=True,
        help_text='Código HTTP de respuesta (200, 404, 500, etc.)'
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name='Dirección IP',
        db_index=True
    )
    user_agent = models.TextField(
        blank=True,
        verbose_name='User Agent'
    )
    response_time_ms = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='Tiempo de Respuesta (ms)',
        help_text='Tiempo que tardó la petición en milisegundos'
    )
    query_params = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Parámetros de Query',
        help_text='Query parameters de la petición'
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        verbose_name='Metadata',
        help_text='Información adicional sobre el acceso'
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Fecha y Hora',
        db_index=True
    )
    
    class Meta:
        verbose_name = 'Registro de Acceso'
        verbose_name_plural = 'Registros de Acceso'
        ordering = ['-timestamp']
        db_table = 'access_logs'
        indexes = [
            models.Index(fields=['-timestamp'], name='idx_access_timestamp'),
            models.Index(fields=['user', '-timestamp'], name='idx_access_user_ts'),
            models.Index(fields=['module', '-timestamp'], name='idx_access_module_ts'),
            models.Index(fields=['status_code', '-timestamp'], name='idx_access_status_ts'),
            models.Index(fields=['ip_address', '-timestamp'], name='idx_access_ip_ts'),
            models.Index(fields=['endpoint'], name='idx_access_endpoint'),
        ]
    
    def __str__(self):
        return f"{self.username} - {self.method} {self.endpoint} [{self.status_code}] ({self.timestamp})"
    
    @property
    def is_error(self):
        """Indica si la petición resultó en error"""
        return self.status_code >= 400
    
    @property
    def is_slow(self):
        """Indica si la petición fue lenta (>2 segundos)"""
        return self.response_time_ms and self.response_time_ms > 2000
