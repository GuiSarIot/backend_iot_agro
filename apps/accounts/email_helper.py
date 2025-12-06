"""
Helper para envío de correos electrónicos con plantillas HTML
Similar a telegram_helper pero para notificaciones por email
"""

from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class EmailNotifier:
    """
    Clase para gestionar el envío de correos electrónicos
    """
    
    def __init__(self):
        self.from_email = settings.DEFAULT_FROM_EMAIL
        self.enabled = getattr(settings, 'EMAIL_NOTIFICATIONS_ENABLED', True)
        self.timeout = getattr(settings, 'EMAIL_TIMEOUT', 10)
    
    def _check_configuration(self):
        """Verifica que la configuración de email esté lista"""
        if not self.enabled:
            return False, "Notificaciones por email deshabilitadas"
        
        if not settings.EMAIL_HOST_USER:
            return False, "EMAIL_HOST_USER no configurado"
        
        if not settings.EMAIL_HOST_PASSWORD:
            return False, "EMAIL_HOST_PASSWORD no configurado"
        
        return True, "Configuración OK"
    
    def send_html_email(self, to_email, subject, html_content, text_content=None):
        """
        Envía un email con contenido HTML y texto plano alternativo
        
        Args:
            to_email (str): Email del destinatario
            subject (str): Asunto del email
            html_content (str): Contenido HTML del email
            text_content (str, optional): Versión en texto plano
        
        Returns:
            tuple: (bool, dict) - (éxito, datos de respuesta)
        """
        is_configured, message = self._check_configuration()
        if not is_configured:
            logger.warning(f"Email no configurado: {message}")
            return False, {'error': message}
        
        try:
            # Si no hay texto plano, generar desde HTML
            if not text_content:
                text_content = strip_tags(html_content)
            
            # Crear email multipart
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=self.from_email,
                to=[to_email]
            )
            email.attach_alternative(html_content, "text/html")
            
            # Enviar
            email.send(fail_silently=False)
            
            logger.info(f"Email enviado exitosamente a {to_email}")
            return True, {'email_sent': True, 'recipient': to_email}
            
        except Exception as e:
            logger.error(f"Error enviando email a {to_email}: {str(e)}")
            return False, {'error': str(e)}
    
    def send_simple_email(self, to_email, subject, message):
        """
        Envía un email simple de texto plano
        
        Args:
            to_email (str): Email del destinatario
            subject (str): Asunto del email
            message (str): Mensaje de texto plano
        
        Returns:
            tuple: (bool, dict) - (éxito, datos de respuesta)
        """
        is_configured, config_message = self._check_configuration()
        if not is_configured:
            logger.warning(f"Email no configurado: {config_message}")
            return False, {'error': config_message}
        
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=self.from_email,
                recipient_list=[to_email],
                fail_silently=False
            )
            
            logger.info(f"Email simple enviado a {to_email}")
            return True, {'email_sent': True, 'recipient': to_email}
            
        except Exception as e:
            logger.error(f"Error enviando email simple a {to_email}: {str(e)}")
            return False, {'error': str(e)}
    
    def send_notification_to_user(self, user, message, notification_type='info', subject=None):
        """
        Envía una notificación por email a un usuario
        
        Args:
            user: Objeto CustomUser
            message (str): Mensaje a enviar
            notification_type (str): Tipo de notificación (success, info, warning, error)
            subject (str, optional): Asunto del email (se genera automáticamente si no se proporciona)
        
        Returns:
            tuple: (bool, dict) - (éxito, datos de respuesta)
        """
        if not user.can_receive_email_notifications:
            logger.info(f"Usuario {user.username} no puede recibir emails")
            return False, {'error': 'Usuario no puede recibir notificaciones por email'}
        
        # Generar asunto si no se proporciona
        if not subject:
            type_subjects = {
                'success': '✅ Notificación IoT Sensor Platform',
                'info': 'ℹ️ Información IoT Sensor Platform',
                'warning': '⚠️ Alerta IoT Sensor Platform',
                'error': '🚨 Error IoT Sensor Platform'
            }
            subject = type_subjects.get(notification_type, 'Notificación IoT Sensor Platform')
        
        # Crear contenido HTML
        html_content = self._generate_notification_html(user, message, notification_type)
        
        return self.send_html_email(user.email, subject, html_content)
    
    def send_notification_to_users(self, users, message, notification_type='info', subject=None):
        """
        Envía notificaciones por email a múltiples usuarios
        
        Args:
            users: QuerySet o lista de objetos CustomUser
            message (str): Mensaje a enviar
            notification_type (str): Tipo de notificación
            subject (str, optional): Asunto del email
        
        Returns:
            dict: Resumen de envíos (exitosos, fallidos)
        """
        results = {
            'sent': 0,
            'failed': 0,
            'errors': []
        }
        
        for user in users:
            success, data = self.send_notification_to_user(user, message, notification_type, subject)
            if success:
                results['sent'] += 1
            else:
                results['failed'] += 1
                results['errors'].append({
                    'user': user.username,
                    'error': data.get('error', 'Unknown error')
                })
        
        logger.info(f"Envío masivo: {results['sent']} exitosos, {results['failed']} fallidos")
        return results
    
    def send_verification_email(self, user, verification_url):
        """
        Envía email de verificación de cuenta
        
        Args:
            user: Objeto CustomUser
            verification_url (str): URL con token de verificación
        
        Returns:
            tuple: (bool, dict)
        """
        subject = "Verifica tu correo electrónico - IoT Sensor Platform"
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .button {{ display: inline-block; padding: 15px 30px; background: #667eea; color: white; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔐 Verifica tu Email</h1>
                </div>
                <div class="content">
                    <p>Hola <strong>{user.username}</strong>,</p>
                    <p>Gracias por registrarte en <strong>IoT Sensor Platform</strong>.</p>
                    <p>Para completar tu registro y activar las notificaciones por correo, por favor verifica tu dirección de email haciendo clic en el botón:</p>
                    <div style="text-align: center;">
                        <a href="{verification_url}" class="button">✅ Verificar Email</a>
                    </div>
                    <p>O copia y pega este enlace en tu navegador:</p>
                    <p style="word-break: break-all; background: #e0e0e0; padding: 10px; border-radius: 5px;">
                        {verification_url}
                    </p>
                    <p><strong>⏰ Este enlace expira en 24 horas.</strong></p>
                    <p>Si no solicitaste esta verificación, puedes ignorar este email.</p>
                </div>
                <div class="footer">
                    <p>IoT Sensor Platform - Sistema de Monitoreo de Sensores</p>
                    <p>Este es un email automático, por favor no respondas.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return self.send_html_email(user.email, subject, html_content)
    
    def send_device_alert(self, device, alert_type, message, recipients=None):
        """
        Envía alerta relacionada con un dispositivo IoT
        
        Args:
            device: Objeto Dispositivo
            alert_type (str): Tipo de alerta (connection, error, warning, info)
            message (str): Mensaje de la alerta
            recipients (list, optional): Lista de usuarios. Si no se proporciona, envía al operador asignado
        
        Returns:
            dict: Resumen de envíos
        """
        if not recipients:
            recipients = [device.operador_asignado] if device.operador_asignado else []
        
        alert_subjects = {
            'connection': f'🔌 Dispositivo {device.nombre} - Estado de Conexión',
            'error': f'🚨 Error en Dispositivo {device.nombre}',
            'warning': f'⚠️ Advertencia Dispositivo {device.nombre}',
            'info': f'ℹ️ Información Dispositivo {device.nombre}'
        }
        
        subject = alert_subjects.get(alert_type, f'Alerta Dispositivo {device.nombre}')
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .alert {{ padding: 20px; border-radius: 10px; margin: 20px 0; }}
                .alert-error {{ background: #fee; border-left: 5px solid #f00; }}
                .alert-warning {{ background: #ffe; border-left: 5px solid #fa0; }}
                .alert-info {{ background: #eff; border-left: 5px solid #0af; }}
                .device-info {{ background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 15px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>Alerta de Dispositivo IoT</h2>
                <div class="alert alert-{alert_type}">
                    <p><strong>📱 Dispositivo:</strong> {device.nombre}</p>
                    <p><strong>🔖 Identificador:</strong> {device.identificador_unico}</p>
                    <p><strong>📍 Ubicación:</strong> {device.ubicacion or 'No especificada'}</p>
                    <p><strong>📊 Estado:</strong> {device.get_estado_display()}</p>
                </div>
                <div style="margin: 20px 0;">
                    <h3>Mensaje:</h3>
                    <p>{message}</p>
                </div>
                <div class="device-info">
                    <p><strong>Información adicional:</strong></p>
                    <p>Tipo: {device.tipo_dispositivo.nombre if device.tipo_dispositivo else 'N/A'}</p>
                    <p>MQTT Habilitado: {'Sí' if device.mqtt_enabled else 'No'}</p>
                    <p>Última conexión: {device.last_seen or 'Nunca'}</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        results = {'sent': 0, 'failed': 0, 'errors': []}
        
        for user in recipients:
            if user and user.can_receive_email_notifications:
                success, data = self.send_html_email(user.email, subject, html_content)
                if success:
                    results['sent'] += 1
                else:
                    results['failed'] += 1
                    results['errors'].append({'user': user.username, 'error': data.get('error')})
        
        return results
    
    def send_reading_alert(self, reading, sensor, threshold_type='exceeded', recipients=None):
        """
        Envía alerta relacionada con una lectura de sensor
        
        Args:
            reading: Objeto Lectura
            sensor: Objeto Sensor
            threshold_type (str): Tipo de umbral (exceeded, critical, normal)
            recipients (list, optional): Lista de usuarios
        
        Returns:
            dict: Resumen de envíos
        """
        if not recipients and sensor.dispositivo and sensor.dispositivo.operador_asignado:
            recipients = [sensor.dispositivo.operador_asignado]
        
        threshold_subjects = {
            'exceeded': f'⚠️ Umbral Excedido - Sensor {sensor.nombre}',
            'critical': f'🚨 Lectura Crítica - Sensor {sensor.nombre}',
            'normal': f'✅ Sensor Normalizado - {sensor.nombre}'
        }
        
        subject = threshold_subjects.get(threshold_type, f'Alerta Sensor {sensor.nombre}')
        
        html_content = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .reading {{ background: #f0f8ff; padding: 20px; border-radius: 10px; margin: 20px 0; border-left: 5px solid #4a90e2; }}
                .value {{ font-size: 24px; font-weight: bold; color: #4a90e2; }}
                .sensor-info {{ background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 15px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <h2>📊 Alerta de Lectura de Sensor</h2>
                <div class="reading">
                    <p><strong>🔬 Sensor:</strong> {sensor.nombre}</p>
                    <p><strong>📏 Tipo:</strong> {sensor.tipo_sensor.nombre if sensor.tipo_sensor else 'N/A'}</p>
                    <p class="value">Valor: {reading.valor} {sensor.unidad_medida or ''}</p>
                    <p><strong>⏰ Timestamp:</strong> {reading.timestamp}</p>
                </div>
                <div class="sensor-info">
                    <p><strong>Información del Sensor:</strong></p>
                    <p>📱 Dispositivo: {sensor.dispositivo.nombre if sensor.dispositivo else 'N/A'}</p>
                    <p>📍 Ubicación: {sensor.ubicacion or 'No especificada'}</p>
                    <p>🔢 Estado: {sensor.get_estado_display()}</p>
                    <p>📡 Intervalo de lectura: {sensor.intervalo_lectura} segundos</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        results = {'sent': 0, 'failed': 0, 'errors': []}
        
        if recipients:
            for user in recipients:
                if user and user.can_receive_email_notifications:
                    success, data = self.send_html_email(user.email, subject, html_content)
                    if success:
                        results['sent'] += 1
                    else:
                        results['failed'] += 1
                        results['errors'].append({'user': user.username, 'error': data.get('error')})
        
        return results
    
    def _generate_notification_html(self, user, message, notification_type):
        """Genera HTML para notificaciones genéricas"""
        type_colors = {
            'success': '#28a745',
            'info': '#17a2b8',
            'warning': '#ffc107',
            'error': '#dc3545'
        }
        
        type_icons = {
            'success': '✅',
            'info': 'ℹ️',
            'warning': '⚠️',
            'error': '🚨'
        }
        
        color = type_colors.get(notification_type, '#17a2b8')
        icon = type_icons.get(notification_type, 'ℹ️')
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: {color}; color: white; padding: 20px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                .footer {{ text-align: center; margin-top: 20px; color: #666; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>{icon} Notificación IoT Sensor Platform</h2>
                </div>
                <div class="content">
                    <p>Hola <strong>{user.username}</strong>,</p>
                    <div style="background: white; padding: 20px; border-radius: 5px; border-left: 5px solid {color};">
                        {message}
                    </div>
                </div>
                <div class="footer">
                    <p>IoT Sensor Platform - Sistema de Monitoreo de Sensores</p>
                    <p>Este es un email automático, por favor no respondas.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html


# Instancia global del notificador
email_notifier = EmailNotifier()
