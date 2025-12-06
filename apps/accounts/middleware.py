"""
Middleware para auditoría y registro de accesos
"""

import time
from django.utils.deprecation import MiddlewareMixin
from django.urls import resolve
from .models import AccessLog
import logging

logger = logging.getLogger(__name__)


class AccessLogMiddleware(MiddlewareMixin):
    """
    Middleware que registra todos los accesos a la API
    """
    
    # Endpoints que NO se deben registrar (para evitar ruido)
    EXCLUDED_PATHS = [
        '/static/',
        '/media/',
        '/favicon.ico',
        '/admin/jsi18n/',
    ]
    
    # Mapeo de endpoints a módulos
    MODULE_MAP = {
        '/api/auth/': 'auth',
        '/api/users/': 'users',
        '/api/roles/': 'roles',
        '/api/permisos/': 'permissions',
        '/api/devices/': 'devices',
        '/api/sensors/': 'sensors',
        '/api/readings/': 'readings',
        '/api/mqtt/': 'mqtt',
        '/api/emqx-users/': 'emqx',
        '/api/emqx-acl/': 'emqx',
        '/admin/': 'admin',
        '/api/docs/': 'api_docs',
        '/api/schema/': 'api_docs',
        '/api/redoc/': 'api_docs',
    }
    
    def process_request(self, request):
        """Marca el tiempo de inicio de la petición"""
        request._start_time = time.time()
        return None
    
    def process_response(self, request, response):
        """Registra el acceso después de procesar la respuesta"""
        
        # Verificar si debe excluirse
        path = request.path
        if any(path.startswith(excluded) for excluded in self.EXCLUDED_PATHS):
            return response
        
        # Solo registrar peticiones a la API
        if not path.startswith('/api/') and not path.startswith('/admin/'):
            return response
        
        # Calcular tiempo de respuesta
        response_time_ms = None
        if hasattr(request, '_start_time'):
            response_time_ms = int((time.time() - request._start_time) * 1000)
        
        # Determinar módulo
        module = self._get_module_from_path(path)
        
        # Obtener información del usuario
        user = None
        username = 'anonymous'
        if hasattr(request, 'user') and request.user.is_authenticated:
            user = request.user
            username = user.username
        
        # Obtener IP
        ip_address = self._get_client_ip(request)
        
        # Obtener user agent
        user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]  # Limitar tamaño
        
        # Obtener query params
        query_params = dict(request.GET.items()) if request.GET else {}
        
        # Crear registro de acceso (de forma asíncrona para no afectar el response)
        try:
            AccessLog.objects.create(
                user=user,
                username=username,
                module=module,
                endpoint=path,
                method=request.method,
                status_code=response.status_code,
                ip_address=ip_address,
                user_agent=user_agent,
                response_time_ms=response_time_ms,
                query_params=query_params,
                metadata={
                    'content_type': request.content_type,
                    'response_reason': getattr(response, 'reason_phrase', ''),
                }
            )
        except Exception as e:
            # No fallar el request si hay error en logging
            logger.error(f"Error al crear AccessLog: {e}")
        
        return response
    
    def _get_module_from_path(self, path):
        """Determina el módulo basado en el path"""
        for prefix, module in self.MODULE_MAP.items():
            if path.startswith(prefix):
                return module
        return 'other'
    
    def _get_client_ip(self, request):
        """Obtiene la IP real del cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class AuditMiddleware(MiddlewareMixin):
    """
    Middleware para auditoría de cambios en modelos críticos
    Se complementa con signals para registrar cambios específicos
    """
    
    def process_request(self, request):
        """Guarda información del request en el thread local para uso en signals"""
        from threading import local
        
        _thread_locals = getattr(self, '_thread_locals', None)
        if _thread_locals is None:
            _thread_locals = local()
            self._thread_locals = _thread_locals
        
        # Guardar info del request para que signals puedan accederla
        _thread_locals.request = request
        _thread_locals.user = getattr(request, 'user', None)
        _thread_locals.ip_address = self._get_client_ip(request)
        _thread_locals.user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        return None
    
    def _get_client_ip(self, request):
        """Obtiene la IP real del cliente"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
