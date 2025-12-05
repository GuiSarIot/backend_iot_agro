"""
URL Configuration para la app Accounts
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    CustomUserViewSet, RolViewSet, PermisoViewSet,
    register_view, login_view, current_user_view, dashboard_stats,
    encrypt_id_view, decrypt_id_view
)

# Router para los ViewSets
router = DefaultRouter()
router.register(r'users', CustomUserViewSet, basename='user')
router.register(r'roles', RolViewSet, basename='role')
router.register(r'permisos', PermisoViewSet, basename='permiso')

urlpatterns = [
    # Autenticacion
    path('auth/register/', register_view, name='register'),
    path('auth/login/', login_view, name='login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Usuario actual
    path('users/me/', current_user_view, name='current-user'),
    
    # Dashboard
    path('dashboard/stats/', dashboard_stats, name='dashboard-stats'),
    
    # Cifrado/Descifrado de IDs
    path('login/cifrar_id/<int:user_id>/', encrypt_id_view, name='encrypt-id'),
    path('login/descifrar_id/', decrypt_id_view, name='decrypt-id'),
    
    # Incluir las rutas del router
    path('', include(router.urls)),
]
