"""
Configuración de la app Readings
"""

from django.apps import AppConfig


class ReadingsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.readings'
    verbose_name = 'Gestión de Lecturas'
