"""
Configuración de la app Sensors
"""

from django.apps import AppConfig


class SensorsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.sensors'
    verbose_name = 'Gestión de Sensores'
