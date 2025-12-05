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
