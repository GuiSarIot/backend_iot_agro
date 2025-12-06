"""
URL Configuration para la app Accounts
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    CustomUserViewSet, RolViewSet, PermisoViewSet,
    register_view, login_view, current_user_view, dashboard_stats,
    encrypt_id_view, decrypt_id_view, AuditLogViewSet, AccessLogViewSet,
    telegram_generate_verification, telegram_verify_code, telegram_link_account,
    telegram_unlink_account, telegram_send_notification, telegram_status,
    email_send_verification, email_verify_token, email_update_preferences,
    email_send_notification, email_status
)

# Router para los ViewSets
router = DefaultRouter()
router.register(r'users', CustomUserViewSet, basename='user')
router.register(r'roles', RolViewSet, basename='role')
router.register(r'permisos', PermisoViewSet, basename='permiso')
router.register(r'audit-logs', AuditLogViewSet, basename='audit-log')
router.register(r'access-logs', AccessLogViewSet, basename='access-log')

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
    
    # Telegram
    path('telegram/generate-verification/', telegram_generate_verification, name='telegram-generate-verification'),
    path('telegram/verify-code/', telegram_verify_code, name='telegram-verify-code'),
    path('telegram/link-account/', telegram_link_account, name='telegram-link-account'),
    path('telegram/unlink-account/', telegram_unlink_account, name='telegram-unlink-account'),
    path('telegram/send-notification/', telegram_send_notification, name='telegram-send-notification'),
    path('telegram/status/', telegram_status, name='telegram-status'),
    
    # Email
    path('email/send-verification/', email_send_verification, name='email-send-verification'),
    path('email/verify/', email_verify_token, name='email-verify-token'),
    path('email/preferences/', email_update_preferences, name='email-update-preferences'),
    path('email/send-notification/', email_send_notification, name='email-send-notification'),
    path('email/status/', email_status, name='email-status'),
    
    # Incluir las rutas del router
    path('', include(router.urls)),
]
