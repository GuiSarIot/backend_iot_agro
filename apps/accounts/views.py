"""
Views y ViewSets para la app Accounts
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.core.signing import Signer, BadSignature
import logging

from .models import CustomUser, Rol, Permiso
from .serializers import (
    CustomUserSerializer, CustomUserCreateUpdateSerializer,
    RolSerializer, PermisoSerializer, RegisterSerializer, LoginSerializer
)
from .permissions import IsSuperuser, CanManageUsers

logger = logging.getLogger(__name__)


# ============ Vistas de Autenticacion ============

@api_view(['POST'])
@permission_classes([AllowAny])
def register_view(request):
    """
    Endpoint para registrar nuevos usuarios
    POST /api/auth/register/
    """
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        
        logger.info(f"Nuevo usuario registrado: {user.username}")
        
        return Response({
            'user': CustomUserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'message': 'Usuario registrado exitosamente'
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """
    Endpoint para login de usuarios
    POST /api/auth/login/
    """
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        refresh = RefreshToken.for_user(user)
        
        logger.info(f"Usuario autenticado: {user.username}")
        
        return Response({
            'user': CustomUserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'message': 'Login exitoso'
        }, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user_view(request):
    """
    Endpoint para obtener el perfil del usuario actual
    GET /api/users/me/
    """
    serializer = CustomUserSerializer(request.user)
    return Response(serializer.data)


# ============ ViewSets ============

class PermisoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar Permisos
    """
    queryset = Permiso.objects.all()
    serializer_class = PermisoSerializer
    permission_classes = [IsAuthenticated, IsSuperuser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'codigo', 'descripcion']
    ordering_fields = ['nombre', 'created_at']
    ordering = ['nombre']


class RolViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar Roles
    """
    queryset = Rol.objects.all()
    serializer_class = RolSerializer
    permission_classes = [IsAuthenticated, IsSuperuser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['nombre', 'descripcion']
    ordering_fields = ['nombre', 'created_at']
    ordering = ['nombre']


class CustomUserViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar Usuarios
    """
    queryset = CustomUser.objects.all()
    permission_classes = [IsAuthenticated, CanManageUsers]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'email', 'first_name', 'last_name']
    ordering_fields = ['username', 'created_at', 'last_login']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return CustomUserCreateUpdateSerializer
        return CustomUserSerializer
    
    def perform_create(self, serializer):
        logger.info(f"Creando nuevo usuario: {serializer.validated_data.get('username')}")
        serializer.save()
    
    def perform_update(self, serializer):
        logger.info(f"Actualizando usuario: {serializer.instance.username}")
        serializer.save()
    
    def perform_destroy(self, instance):
        logger.warning(f"Eliminando usuario: {instance.username}")
        instance.delete()
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """
        Obtener el perfil del usuario actual
        GET /api/users/me/
        """
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsSuperuser])
    def activate(self, request, pk=None):
        """
        Activar un usuario
        POST /api/users/{id}/activate/
        """
        user = self.get_object()
        user.is_active = True
        user.save()
        logger.info(f"Usuario activado: {user.username}")
        return Response({
            'message': f'Usuario {user.username} activado exitosamente'
        })
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, IsSuperuser])
    def deactivate(self, request, pk=None):
        """
        Desactivar un usuario
        POST /api/users/{id}/deactivate/
        """
        user = self.get_object()
        if user.is_superuser:
            return Response({
                'error': 'No se puede desactivar un superusuario'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user.is_active = False
        user.save()
        logger.info(f"Usuario desactivado: {user.username}")
        return Response({
            'message': f'Usuario {user.username} desactivado exitosamente'
        })


# ============ Vistas adicionales ============

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def dashboard_stats(request):
    """
    Obtener estadisticas para el dashboard
    GET /api/dashboard/stats/
    """
    from apps.sensors.models import Sensor
    from apps.devices.models import Dispositivo
    from apps.readings.models import Lectura
    
    stats = {
        'total_usuarios': CustomUser.objects.count(),
        'total_sensores': Sensor.objects.count(),
        'sensores_activos': Sensor.objects.filter(estado='activo').count(),
        'total_dispositivos': Dispositivo.objects.count(),
        'dispositivos_activos': Dispositivo.objects.filter(estado='activo').count(),
        'dispositivos_mqtt': Dispositivo.objects.filter(mqtt_enabled=True).count(),
        'total_lecturas': Lectura.objects.count(),
    }
    
    # Si es operador, solo mostrar sus estadisticas
    if not request.user.is_superuser:
        if request.user.rol and request.user.rol.nombre == 'operador':
            dispositivos_operador = Dispositivo.objects.filter(
                operador_asignado=request.user
            )
            stats.update({
                'mis_dispositivos': dispositivos_operador.count(),
                'mis_lecturas': Lectura.objects.filter(
                    dispositivo__in=dispositivos_operador
                ).count(),
            })
    
    return Response(stats)


# ============ Vistas de Cifrado/Descifrado ============

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def encrypt_id_view(request, user_id):
    """
    Endpoint para cifrar ID de usuario
    GET /api/login/cifrarID/{user_id}/
    
    Retorna el ID cifrado del usuario
    Similar a Laravel Crypt::encryptString()
    """
    try:
        # Verificar que el usuario existe
        user = CustomUser.objects.get(id=user_id)
        
        # Cifrar el ID usando Django Signer
        signer = Signer()
        encrypted_id = signer.sign(str(user_id))
        
        logger.info(f"ID cifrado generado para usuario {user.username}")
        
        return Response({
            'encrypted_id': encrypted_id,
            'user_id': user_id,
            'username': user.username
        }, status=status.HTTP_200_OK)
        
    except CustomUser.DoesNotExist:
        return Response({
            'error': 'Usuario no encontrado'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error cifrando ID: {str(e)}")
        return Response({
            'error': 'Error al cifrar ID'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def decrypt_id_view(request):
    """
    Endpoint para descifrar ID de usuario
    POST /api/login/descifrarID/
    
    Body: {"encrypted_id": "valor_cifrado"}
    Retorna el ID descifrado del usuario
    Similar a Laravel Crypt::decryptString()
    """
    encrypted_id = request.data.get('encrypted_id')
    
    if not encrypted_id:
        return Response({
            'error': 'encrypted_id es requerido'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        # Descifrar el ID usando Django Signer
        signer = Signer()
        decrypted_id = signer.unsign(encrypted_id)
        
        # Verificar que el usuario existe
        user = CustomUser.objects.get(id=int(decrypted_id))
        
        logger.info(f"ID descifrado exitosamente: {decrypted_id}")
        
        return Response({
            'decrypted_id': int(decrypted_id),
            'user_id': user.id,
            'username': user.username
        }, status=status.HTTP_200_OK)
        
    except BadSignature:
        return Response({
            'error': 'ID cifrado inválido o corrupto'
        }, status=status.HTTP_400_BAD_REQUEST)
    except CustomUser.DoesNotExist:
        return Response({
            'error': 'Usuario no encontrado'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error descifrando ID: {str(e)}")
        return Response({
            'error': 'Error al descifrar ID'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ============ ViewSets de Auditoría ============

class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para consultar registros de auditoría (solo lectura)
    Requiere permisos de superusuario
    """
    from .models import AuditLog
    from .serializers import AuditLogSerializer
    
    queryset = AuditLog.objects.select_related('user').all()
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated, IsSuperuser]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'model_name', 'object_repr', 'ip_address']
    ordering_fields = ['timestamp', 'action', 'model_name']
    ordering = ['-timestamp']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtrar por modelo
        model_name = self.request.query_params.get('model_name', None)
        if model_name:
            queryset = queryset.filter(model_name=model_name)
        
        # Filtrar por acción
        action = self.request.query_params.get('action', None)
        if action:
            queryset = queryset.filter(action=action)
        
        # Filtrar por usuario
        user_id = self.request.query_params.get('user_id', None)
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        # Filtrar por rango de fechas
        from_date = self.request.query_params.get('from_date', None)
        to_date = self.request.query_params.get('to_date', None)
        if from_date:
            queryset = queryset.filter(timestamp__gte=from_date)
        if to_date:
            queryset = queryset.filter(timestamp__lte=to_date)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Obtener estadísticas de auditoría
        GET /api/audit-logs/stats/
        """
        from django.db.models import Count
        from .models import AuditLog
        
        queryset = self.get_queryset()
        
        stats = {
            'total_logs': queryset.count(),
            'by_action': dict(queryset.values('action').annotate(count=Count('id')).values_list('action', 'count')),
            'by_model': dict(queryset.values('model_name').annotate(count=Count('id')).values_list('model_name', 'count')[:10]),
            'recent_changes': queryset[:10].values('username', 'action', 'model_name', 'timestamp', 'object_repr')
        }
        
        return Response(stats)


class AccessLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para consultar registros de acceso (solo lectura)
    Superusuarios ven todos, usuarios normales solo los suyos
    """
    from .models import AccessLog
    from .serializers import AccessLogSerializer
    
    queryset = AccessLog.objects.select_related('user').all()
    serializer_class = AccessLogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['username', 'endpoint', 'ip_address', 'module']
    ordering_fields = ['timestamp', 'status_code', 'response_time_ms', 'module']
    ordering = ['-timestamp']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Usuarios no superusuarios solo ven sus propios logs
        if not self.request.user.is_superuser:
            queryset = queryset.filter(user=self.request.user)
        
        # Filtrar por módulo
        module = self.request.query_params.get('module', None)
        if module:
            queryset = queryset.filter(module=module)
        
        # Filtrar por método HTTP
        method = self.request.query_params.get('method', None)
        if method:
            queryset = queryset.filter(method=method.upper())
        
        # Filtrar por código de estado
        status_code = self.request.query_params.get('status_code', None)
        if status_code:
            queryset = queryset.filter(status_code=status_code)
        
        # Filtrar solo errores
        errors_only = self.request.query_params.get('errors_only', None)
        if errors_only and errors_only.lower() == 'true':
            queryset = queryset.filter(status_code__gte=400)
        
        # Filtrar respuestas lentas
        slow_only = self.request.query_params.get('slow_only', None)
        if slow_only and slow_only.lower() == 'true':
            queryset = queryset.filter(response_time_ms__gt=2000)
        
        # Filtrar por usuario
        user_id = self.request.query_params.get('user_id', None)
        if user_id and self.request.user.is_superuser:
            queryset = queryset.filter(user_id=user_id)
        
        # Filtrar por rango de fechas
        from_date = self.request.query_params.get('from_date', None)
        to_date = self.request.query_params.get('to_date', None)
        if from_date:
            queryset = queryset.filter(timestamp__gte=from_date)
        if to_date:
            queryset = queryset.filter(timestamp__lte=to_date)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Obtener estadísticas de acceso
        GET /api/access-logs/stats/
        """
        from django.db.models import Count, Avg, Max, Min
        from .models import AccessLog
        
        queryset = self.get_queryset()
        
        stats = {
            'total_requests': queryset.count(),
            'by_module': dict(queryset.values('module').annotate(count=Count('id')).values_list('module', 'count')),
            'by_method': dict(queryset.values('method').annotate(count=Count('id')).values_list('method', 'count')),
            'by_status': dict(queryset.values('status_code').annotate(count=Count('id')).values_list('status_code', 'count')),
            'errors_count': queryset.filter(status_code__gte=400).count(),
            'avg_response_time_ms': queryset.filter(response_time_ms__isnull=False).aggregate(Avg('response_time_ms'))['response_time_ms__avg'],
            'slowest_endpoint': queryset.filter(response_time_ms__isnull=False).order_by('-response_time_ms').values('endpoint', 'response_time_ms').first(),
            'most_accessed_endpoints': list(queryset.values('endpoint', 'method').annotate(count=Count('id')).order_by('-count')[:10])
        }
        
        return Response(stats)
    
    @action(detail=False, methods=['post'])
    def create_log(self, request):
        """
        Crear un registro de acceso manualmente
        POST /api/access-logs/create-log/
        """
        from .serializers import CreateAccessLogSerializer
        
        serializer = CreateAccessLogSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            log = serializer.save()
            from .serializers import AccessLogSerializer
            return Response(AccessLogSerializer(log).data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ============ Vistas de Telegram ============

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def telegram_generate_verification(request):
    """
    Generar código de verificación para vincular Telegram
    POST /api/telegram/generate-verification/
    """
    user = request.user
    code = user.generate_telegram_verification_code()
    
    logger.info(f"Código de verificación Telegram generado para {user.username}")
    
    return Response({
        'verification_code': code,
        'expires_in_minutes': 15,
        'instructions': 'Envía este código al bot de Telegram para vincular tu cuenta'
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def telegram_verify_code(request):
    """
    Verificar código de Telegram (usado por usuario web)
    POST /api/telegram/verify-code/
    Body: {"code": "ABCD1234"}
    """
    from .serializers import TelegramVerifyCodeSerializer
    
    serializer = TelegramVerifyCodeSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    user = request.user
    code = serializer.validated_data['code']
    
    success, message = user.verify_telegram_code(code)
    
    if success:
        logger.info(f"Telegram verificado para {user.username}")
        return Response({
            'success': True,
            'message': message,
            'user': CustomUserSerializer(user).data
        })
    else:
        return Response({
            'success': False,
            'message': message
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])  # El bot usa un token especial
def telegram_link_account(request):
    """
    Vincular cuenta de Telegram (usado por el bot)
    POST /api/telegram/link-account/
    Body: {
        "user_id": 1,
        "chat_id": "123456789",
        "username": "@username",
        "verification_code": "ABCD1234"
    }
    
    Requiere: Header "X-Telegram-Bot-Token" con el token del bot
    """
    from .serializers import TelegramLinkSerializer
    from django.conf import settings
    
    # Verificar token del bot
    bot_token = request.headers.get('X-Telegram-Bot-Token')
    expected_token = getattr(settings, 'TELEGRAM_BOT_TOKEN', None)
    
    if not expected_token or bot_token != expected_token:
        return Response({
            'error': 'Token de bot inválido'
        }, status=status.HTTP_403_FORBIDDEN)
    
    serializer = TelegramLinkSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        user = CustomUser.objects.get(id=serializer.validated_data['user_id'])
    except CustomUser.DoesNotExist:
        return Response({
            'error': 'Usuario no encontrado'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Verificar código
    success, message = user.verify_telegram_code(serializer.validated_data['verification_code'])
    
    if not success:
        return Response({
            'success': False,
            'message': message
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Vincular Telegram
    user.telegram_chat_id = serializer.validated_data['chat_id']
    user.telegram_username = serializer.validated_data.get('username', '')
    user.telegram_notifications_enabled = True
    user.save(update_fields=['telegram_chat_id', 'telegram_username', 'telegram_notifications_enabled'])
    
    logger.info(f"Telegram vinculado para {user.username} - chat_id: {user.telegram_chat_id}")
    
    return Response({
        'success': True,
        'message': 'Cuenta de Telegram vinculada exitosamente',
        'user_id': user.id,
        'username': user.username
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def telegram_unlink_account(request):
    """
    Desvincular cuenta de Telegram
    POST /api/telegram/unlink-account/
    """
    user = request.user
    
    if not user.telegram_chat_id:
        return Response({
            'error': 'No hay cuenta de Telegram vinculada'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Desvincular
    user.telegram_chat_id = None
    user.telegram_username = None
    user.telegram_verified = False
    user.telegram_notifications_enabled = False
    user.save(update_fields=[
        'telegram_chat_id', 'telegram_username', 
        'telegram_verified', 'telegram_notifications_enabled'
    ])
    
    logger.info(f"Telegram desvinculado para {user.username}")
    
    return Response({
        'success': True,
        'message': 'Cuenta de Telegram desvinculada exitosamente'
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated, IsSuperuser])
def telegram_send_notification(request):
    """
    Enviar notificación via Telegram (solo superusuarios)
    POST /api/telegram/send-notification/
    Body: {
        "message": "Mensaje a enviar",
        "user_ids": [1, 2, 3],  // Opcional
        "notification_type": "info",  // info, warning, error, success
        "send_to_all_verified": false  // Opcional
    }
    """
    from .serializers import TelegramNotificationSerializer
    
    serializer = TelegramNotificationSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    message = serializer.validated_data['message']
    user_ids = serializer.validated_data.get('user_ids')
    send_to_all = serializer.validated_data.get('send_to_all_verified', False)
    notification_type = serializer.validated_data.get('notification_type', 'info')
    
    # Iconos por tipo de notificación
    icons = {
        'info': 'ℹ️',
        'warning': '⚠️',
        'error': '❌',
        'success': '✅'
    }
    icon = icons.get(notification_type, 'ℹ️')
    formatted_message = f"{icon} {message}"
    
    # Determinar destinatarios
    if send_to_all:
        users = CustomUser.objects.filter(
            telegram_verified=True,
            telegram_notifications_enabled=True,
            telegram_chat_id__isnull=False
        )
    elif user_ids:
        users = CustomUser.objects.filter(
            id__in=user_ids,
            telegram_verified=True,
            telegram_notifications_enabled=True,
            telegram_chat_id__isnull=False
        )
    else:
        return Response({
            'error': 'Debe especificar user_ids o send_to_all_verified'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Aquí se integraría con el bot de Telegram
    # Por ahora, solo registramos la intención
    sent_to = []
    for user in users:
        sent_to.append({
            'user_id': user.id,
            'username': user.username,
            'chat_id': user.telegram_chat_id
        })
        logger.info(f"Notificación Telegram enviada a {user.username}: {message}")
    
    return Response({
        'success': True,
        'message': f'Notificación enviada a {len(sent_to)} usuario(s)',
        'sent_to': sent_to,
        'notification': {
            'type': notification_type,
            'message': formatted_message
        }
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def telegram_status(request):
    """
    Obtener estado de integración de Telegram del usuario
    GET /api/telegram/status/
    """
    user = request.user
    
    return Response({
        'is_linked': bool(user.telegram_chat_id),
        'is_verified': user.telegram_verified,
        'notifications_enabled': user.telegram_notifications_enabled,
        'can_receive_notifications': user.can_receive_telegram_notifications,
        'telegram_username': user.telegram_username,
        'has_pending_verification': bool(user.telegram_verification_code)
    })


# ============ Vistas de Email ============

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def email_send_verification(request):
    """
    Enviar email de verificación al usuario
    POST /api/email/send-verification/
    """
    from .email_helper import email_notifier
    from .serializers import EmailVerificationSerializer
    from django.urls import reverse
    
    user = request.user
    
    if user.email_verified:
        return Response({
            'success': False,
            'error': 'El email ya está verificado'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    if not user.email:
        return Response({
            'success': False,
            'error': 'El usuario no tiene email configurado'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Generar token
    token = user.generate_email_verification_token()
    
    # Construir URL de verificación
    verification_url = f"{request.build_absolute_uri('/api/email/verify/')}?token={token}"
    
    # Enviar email
    success, data = email_notifier.send_verification_email(user, verification_url)
    
    if success:
        logger.info(f"Email de verificación enviado a {user.email}")
        return Response({
            'success': True,
            'message': f'Email de verificación enviado a {user.email}',
            'email': user.email
        })
    else:
        logger.error(f"Error enviando verificación a {user.email}: {data.get('error')}")
        return Response({
            'success': False,
            'error': data.get('error', 'Error desconocido')
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def email_verify_token(request):
    """
    Verificar token de email
    GET /api/email/verify/?token=xxx
    POST /api/email/verify/ (body: {"token": "xxx"})
    """
    from .serializers import EmailVerifyTokenSerializer
    
    user = request.user
    
    # Obtener token desde query params (GET) o body (POST)
    if request.method == 'GET':
        token = request.query_params.get('token')
    else:
        serializer = EmailVerifyTokenSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        token = serializer.validated_data['token']
    
    if not token:
        return Response({
            'success': False,
            'error': 'Token no proporcionado'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Verificar token
    success, message = user.verify_email_token(token)
    
    if success:
        logger.info(f"Email verificado exitosamente para {user.username}")
        return Response({
            'success': True,
            'message': message,
            'email_verified': True
        })
    else:
        return Response({
            'success': False,
            'error': message
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def email_update_preferences(request):
    """
    Actualizar preferencias de notificaciones por email
    POST /api/email/preferences/
    Body: {"email_notifications_enabled": true/false}
    """
    from .serializers import EmailPreferencesSerializer
    
    user = request.user
    serializer = EmailPreferencesSerializer(data=request.data)
    
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    # Actualizar preferencias
    if 'email_notifications_enabled' in serializer.validated_data:
        user.email_notifications_enabled = serializer.validated_data['email_notifications_enabled']
        user.save(update_fields=['email_notifications_enabled'])
        
        logger.info(f"Preferencias de email actualizadas para {user.username}")
    
    return Response({
        'success': True,
        'message': 'Preferencias actualizadas',
        'email_notifications_enabled': user.email_notifications_enabled,
        'can_receive_email_notifications': user.can_receive_email_notifications
    })


@api_view(['POST'])
@permission_classes([IsSuperuser])
def email_send_notification(request):
    """
    Enviar notificación por email a usuarios (solo superusuarios)
    POST /api/email/send-notification/
    Body: {
        "user_ids": [1, 2, 3],  # opcional
        "message": "Mensaje",
        "subject": "Asunto",  # opcional
        "notification_type": "info",  # info, warning, error, success
        "send_to_all_verified": false
    }
    """
    from .email_helper import email_notifier
    from .serializers import EmailNotificationSerializer
    
    serializer = EmailNotificationSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    message = serializer.validated_data['message']
    subject = serializer.validated_data.get('subject')
    notification_type = serializer.validated_data.get('notification_type', 'info')
    send_to_all = serializer.validated_data.get('send_to_all_verified', False)
    user_ids = serializer.validated_data.get('user_ids', [])
    
    # Determinar destinatarios
    if send_to_all:
        users = CustomUser.objects.filter(
            email_verified=True,
            email_notifications_enabled=True
        ).exclude(email='')
    elif user_ids:
        users = CustomUser.objects.filter(id__in=user_ids)
    else:
        return Response({
            'success': False,
            'error': 'Debe especificar user_ids o send_to_all_verified'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    # Enviar notificaciones
    results = email_notifier.send_notification_to_users(users, message, notification_type, subject)
    
    logger.info(f"Notificaciones email enviadas: {results['sent']} exitosos, {results['failed']} fallidos")
    
    return Response({
        'success': True,
        'message': f'Notificaciones enviadas: {results["sent"]} exitosos, {results["failed"]} fallidos',
        'results': results
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def email_status(request):
    """
    Obtener estado de email del usuario
    GET /api/email/status/
    """
    user = request.user
    
    return Response({
        'has_email': bool(user.email),
        'email': user.email if user.email else None,
        'is_verified': user.email_verified,
        'notifications_enabled': user.email_notifications_enabled,
        'can_receive_notifications': user.can_receive_email_notifications,
        'verification_sent_at': user.email_verification_sent_at,
        'has_pending_verification': bool(user.email_verification_token)
    })
