"""
Configuración de la app MQTT
"""

from django.apps import AppConfig


class MqttConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.mqtt'
    verbose_name = 'Configuración MQTT/EMQX'
    
    def ready(self):
        """
        Importar señales cuando la aplicación esté lista
        """
        import apps.mqtt.signals  # noqa
