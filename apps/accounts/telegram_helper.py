"""
Helper para enviar notificaciones via Telegram
"""

import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


class TelegramNotifier:
    """
    Clase para enviar notificaciones via Telegram
    """
    
    def __init__(self):
        self.bot_token = settings.TELEGRAM_BOT_TOKEN
        self.base_url = f"https://api.telegram.org/bot{self.bot_token}"
    
    def send_message(self, chat_id, message, parse_mode='HTML'):
        """
        Envía un mensaje a un chat específico
        
        Args:
            chat_id: ID del chat de Telegram
            message: Mensaje a enviar
            parse_mode: Formato del mensaje (HTML, Markdown)
        
        Returns:
            tuple: (success: bool, response: dict)
        """
        if not self.bot_token:
            logger.error("TELEGRAM_BOT_TOKEN no configurado")
            return False, {"error": "Bot token no configurado"}
        
        url = f"{self.base_url}/sendMessage"
        payload = {
            'chat_id': chat_id,
            'text': message,
            'parse_mode': parse_mode
        }
        
        try:
            response = requests.post(url, json=payload, timeout=10)
            response_data = response.json()
            
            if response.status_code == 200 and response_data.get('ok'):
                logger.info(f"Mensaje Telegram enviado a {chat_id}")
                return True, response_data
            else:
                logger.error(f"Error enviando mensaje Telegram: {response_data}")
                return False, response_data
        
        except requests.RequestException as e:
            logger.error(f"Error de conexión con Telegram API: {e}")
            return False, {"error": str(e)}
    
    def send_notification_to_user(self, user, message, notification_type='info'):
        """
        Envía notificación a un usuario específico
        
        Args:
            user: Instancia de CustomUser
            message: Mensaje a enviar
            notification_type: Tipo de notificación (info, warning, error, success)
        
        Returns:
            tuple: (success: bool, response: dict)
        """
        if not user.can_receive_telegram_notifications:
            return False, {"error": "Usuario no puede recibir notificaciones"}
        
        # Iconos por tipo
        icons = {
            'info': 'ℹ️',
            'warning': '⚠️',
            'error': '❌',
            'success': '✅'
        }
        icon = icons.get(notification_type, 'ℹ️')
        
        formatted_message = f"{icon} <b>{notification_type.upper()}</b>\n\n{message}"
        
        return self.send_message(user.telegram_chat_id, formatted_message)
    
    def send_notification_to_users(self, users, message, notification_type='info'):
        """
        Envía notificación a múltiples usuarios
        
        Args:
            users: QuerySet o lista de CustomUser
            message: Mensaje a enviar
            notification_type: Tipo de notificación
        
        Returns:
            dict: Resultados del envío {success: [], failed: []}
        """
        results = {'success': [], 'failed': []}
        
        for user in users:
            success, response = self.send_notification_to_user(user, message, notification_type)
            
            if success:
                results['success'].append({
                    'user_id': user.id,
                    'username': user.username,
                    'chat_id': user.telegram_chat_id
                })
            else:
                results['failed'].append({
                    'user_id': user.id,
                    'username': user.username,
                    'error': response.get('error', 'Unknown error')
                })
        
        return results
    
    def send_device_alert(self, device, alert_type, message):
        """
        Envía alerta relacionada con dispositivo IoT
        
        Args:
            device: Instancia de Dispositivo
            alert_type: Tipo de alerta (offline, error, warning, etc.)
            message: Mensaje de alerta
        """
        from apps.accounts.models import CustomUser
        
        # Enviar al operador asignado
        if device.operador_asignado and device.operador_asignado.can_receive_telegram_notifications:
            alert_message = f"""
🔧 <b>Alerta de Dispositivo</b>

<b>Dispositivo:</b> {device.nombre}
<b>Tipo:</b> {alert_type.upper()}
<b>Ubicación:</b> {device.ubicacion}

<b>Detalle:</b>
{message}
"""
            self.send_notification_to_user(
                device.operador_asignado,
                alert_message,
                'warning' if alert_type == 'offline' else 'error'
            )
        
        # Enviar a todos los superusuarios
        superusers = CustomUser.objects.filter(
            is_superuser=True,
            telegram_verified=True,
            telegram_notifications_enabled=True
        )
        
        for superuser in superusers:
            self.send_notification_to_user(superuser, alert_message, 'warning')
    
    def send_reading_alert(self, reading, sensor, threshold_type):
        """
        Envía alerta de lectura fuera de rango
        
        Args:
            reading: Instancia de Lectura
            sensor: Instancia de Sensor
            threshold_type: 'min' o 'max'
        """
        device = reading.dispositivo
        
        if device.operador_asignado and device.operador_asignado.can_receive_telegram_notifications:
            alert_message = f"""
📊 <b>Alerta de Lectura</b>

<b>Dispositivo:</b> {device.nombre}
<b>Sensor:</b> {sensor.nombre}
<b>Valor:</b> {reading.valor} {sensor.unidad_medida}

<b>Rango permitido:</b> {sensor.rango_min} - {sensor.rango_max} {sensor.unidad_medida}

⚠️ Valor {'por debajo del mínimo' if threshold_type == 'min' else 'por encima del máximo'} permitido.
"""
            self.send_notification_to_user(
                device.operador_asignado,
                alert_message,
                'warning'
            )


# Instancia global
telegram_notifier = TelegramNotifier()
