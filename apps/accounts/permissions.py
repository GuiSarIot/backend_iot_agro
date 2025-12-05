"""
Permisos personalizados para la plataforma IoT Sensor Platform
"""

from rest_framework import permissions


class IsSuperuser(permissions.BasePermission):
    """
    Permiso que solo permite acceso a superusuarios
    """
    message = 'Solo los superusuarios pueden realizar esta acción.'
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_superuser


class IsOperatorOrReadOnly(permissions.BasePermission):
    """
    Permiso que permite a los operadores editar sus recursos y a otros solo lectura
    """
    message = 'Los operadores pueden editar sus recursos, otros usuarios solo tienen acceso de lectura.'
    
    def has_permission(self, request, view):
        # Permitir lectura a todos los usuarios autenticados
        if request.method in permissions.SAFE_METHODS:
            return request.user and request.user.is_authenticated
        
        # Permitir escritura a superusuarios y operadores
        if request.user and request.user.is_authenticated:
            if request.user.is_superuser:
                return True
            if request.user.rol and request.user.rol.nombre == 'operador':
                return True
        
        return False
    
    def has_object_permission(self, request, view, obj):
        # Permitir lectura a todos los usuarios autenticados
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Superusuarios tienen acceso completo
        if request.user.is_superuser:
            return True
        
        # Operadores solo pueden editar sus propios recursos
        if hasattr(obj, 'operador_asignado'):
            return obj.operador_asignado == request.user
        
        return False


class IsOwnerOrSuperuser(permissions.BasePermission):
    """
    Permiso que solo permite al dueño del recurso o a superusuarios modificarlo
    """
    message = 'Solo el dueño del recurso o un superusuario puede modificarlo.'
    
    def has_object_permission(self, request, view, obj):
        # Permitir lectura a todos los usuarios autenticados
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Superusuarios tienen acceso completo
        if request.user.is_superuser:
            return True
        
        # El dueño del recurso puede modificarlo
        if hasattr(obj, 'created_by'):
            return obj.created_by == request.user
        
        # Para el modelo CustomUser, permitir que el usuario edite su propio perfil
        if hasattr(obj, 'username'):
            return obj == request.user
        
        return False


class IsSuperuserOrOperator(permissions.BasePermission):
    """
    Permiso que permite acceso a superusuarios y operadores
    """
    message = 'Solo los superusuarios y operadores pueden realizar esta acción.'
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if request.user.is_superuser:
            return True
        
        if request.user.rol and request.user.rol.nombre in ['operador', 'superusuario']:
            return True
        
        return False


class ReadOnlyPermission(permissions.BasePermission):
    """
    Permiso que solo permite operaciones de lectura
    """
    message = 'Esta acción es de solo lectura.'
    
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


class CanManageUsers(permissions.BasePermission):
    """
    Permiso para gestionar usuarios (solo superusuarios)
    """
    message = 'Solo los superusuarios pueden gestionar usuarios.'
    
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_superuser


class CanManageSensors(permissions.BasePermission):
    """
    Permiso para gestionar sensores (superusuarios y operadores)
    """
    message = 'No tiene permisos para gestionar sensores.'
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Lectura para todos
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Escritura solo para superusuarios y operadores
        if request.user.is_superuser:
            return True
        
        if request.user.rol and request.user.rol.nombre in ['operador', 'superusuario']:
            return True
        
        return False


class CanManageDevices(permissions.BasePermission):
    """
    Permiso para gestionar dispositivos
    """
    message = 'No tiene permisos para gestionar dispositivos.'
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Lectura para todos
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Escritura solo para superusuarios
        if request.user.is_superuser:
            return True
        
        # Los operadores pueden gestionar sus propios dispositivos
        if request.user.rol and request.user.rol.nombre == 'operador':
            return True
        
        return False
    
    def has_object_permission(self, request, view, obj):
        # Lectura para todos
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Superusuarios tienen acceso completo
        if request.user.is_superuser:
            return True
        
        # Operadores solo pueden modificar sus dispositivos asignados
        if request.user.rol and request.user.rol.nombre == 'operador':
            return obj.operador_asignado == request.user
        
        return False


class CanCreateReadings(permissions.BasePermission):
    """
    Permiso para crear lecturas de sensores
    """
    message = 'No tiene permisos para crear lecturas.'
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Lectura para todos
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Crear lecturas: superusuarios, operadores y dispositivos IoT
        if request.user.is_superuser:
            return True
        
        if request.user.rol and request.user.rol.nombre in ['operador', 'superusuario']:
            return True
        
        return False


class CanManageMQTT(permissions.BasePermission):
    """
    Permiso para gestionar configuración MQTT/EMQX
    """
    message = 'Solo los superusuarios pueden gestionar la configuración MQTT.'
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Lectura para operadores y superusuarios
        if request.method in permissions.SAFE_METHODS:
            if request.user.is_superuser:
                return True
            if request.user.rol and request.user.rol.nombre in ['operador', 'superusuario']:
                return True
            return False
        
        # Escritura solo para superusuarios
        return request.user.is_superuser


class CanViewMQTTCredentials(permissions.BasePermission):
    """
    Permiso para ver credenciales MQTT
    """
    message = 'No tiene permisos para ver credenciales MQTT.'
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Solo superusuarios pueden ver credenciales completas
        if request.user.is_superuser:
            return True
        
        # Operadores pueden ver sus propias credenciales (limitado)
        if request.user.rol and request.user.rol.nombre == 'operador':
            return True
        
        return False
    
    def has_object_permission(self, request, view, obj):
        # Superusuarios tienen acceso completo
        if request.user.is_superuser:
            return True
        
        # Operadores solo pueden ver credenciales de sus dispositivos
        if hasattr(obj, 'dispositivo'):
            return obj.dispositivo.operador_asignado == request.user
        
        return False
