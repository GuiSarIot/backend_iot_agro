"""
Management command para generar una clave de encriptación MQTT segura
"""

from django.core.management.base import BaseCommand
from cryptography.fernet import Fernet


class Command(BaseCommand):
    help = 'Genera una clave de encriptación segura para contraseñas MQTT'
    
    def handle(self, *args, **options):
        # Generar nueva clave Fernet
        key = Fernet.generate_key()
        
        self.stdout.write(self.style.SUCCESS('\n' + '='*70))
        self.stdout.write(self.style.SUCCESS('NUEVA CLAVE DE ENCRIPTACIÓN MQTT GENERADA'))
        self.stdout.write(self.style.SUCCESS('='*70))
        self.stdout.write('')
        self.stdout.write('Copia esta clave y agrégala a tu archivo .env:')
        self.stdout.write('')
        self.stdout.write(self.style.WARNING(f'MQTT_ENCRYPTION_KEY={key.decode()}'))
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('='*70))
        self.stdout.write('')
        self.stdout.write(self.style.WARNING('⚠️  IMPORTANTE:'))
        self.stdout.write('1. Guarda esta clave de forma SEGURA')
        self.stdout.write('2. NO compartas esta clave en repositorios públicos')
        self.stdout.write('3. Si cambias la clave, las contraseñas encriptadas anteriormente no podrán ser desencriptadas')
        self.stdout.write('4. Usa una clave diferente para cada entorno (dev, staging, production)')
        self.stdout.write('')
