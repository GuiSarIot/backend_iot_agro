"""
Management command para migrar contraseñas MQTT existentes a formato encriptado
"""

from django.core.management.base import BaseCommand
from apps.mqtt.models import BrokerConfig, MQTTCredential
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Migra contraseñas MQTT existentes de texto plano a formato encriptado'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Solo muestra qué se haría sin ejecutar cambios',
        )
    
    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('\n🔍 MODO DRY-RUN - No se realizarán cambios\n'))
        
        self.stdout.write(self.style.SUCCESS('='*70))
        self.stdout.write(self.style.SUCCESS('MIGRACIÓN DE CONTRASEÑAS MQTT A FORMATO ENCRIPTADO'))
        self.stdout.write(self.style.SUCCESS('='*70))
        self.stdout.write('')
        
        # Migrar BrokerConfig
        self.stdout.write(self.style.WARNING('📋 Procesando BrokerConfig...'))
        brokers = BrokerConfig.objects.exclude(password__isnull=True).exclude(password='')
        brokers_count = brokers.count()
        
        self.stdout.write(f'Encontrados {brokers_count} brokers con contraseñas')
        
        if not dry_run and brokers_count > 0:
            for broker in brokers:
                try:
                    # Intentar desencriptar para verificar si ya está encriptada
                    decrypted = broker.get_password()
                    if decrypted:
                        self.stdout.write(f'  ✓ {broker.nombre} - ya encriptada')
                        continue
                except Exception:
                    # Si falla, es texto plano, encriptar
                    old_password = broker.password
                    broker.set_password(old_password)
                    broker.save()
                    self.stdout.write(self.style.SUCCESS(f'  ✓ {broker.nombre} - migrada'))
                    logger.info(f'Contraseña migrada para broker: {broker.nombre}')
        
        # Migrar MQTTCredential
        self.stdout.write('')
        self.stdout.write(self.style.WARNING('📋 Procesando MQTTCredential...'))
        credentials = MQTTCredential.objects.exclude(password__isnull=True).exclude(password='')
        credentials_count = credentials.count()
        
        self.stdout.write(f'Encontradas {credentials_count} credenciales con contraseñas')
        
        if not dry_run and credentials_count > 0:
            for cred in credentials:
                try:
                    # Intentar desencriptar para verificar si ya está encriptada
                    decrypted = cred.get_password()
                    if decrypted:
                        self.stdout.write(f'  ✓ {cred.client_id} - ya encriptada')
                        continue
                except Exception:
                    # Si falla, es texto plano, encriptar
                    old_password = cred.password
                    cred.set_password(old_password)
                    cred.save()
                    self.stdout.write(self.style.SUCCESS(f'  ✓ {cred.client_id} - migrada'))
                    logger.info(f'Contraseña migrada para credencial: {cred.client_id}')
        
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('='*70))
        if dry_run:
            self.stdout.write(self.style.WARNING('🔍 DRY-RUN COMPLETADO - No se realizaron cambios'))
        else:
            self.stdout.write(self.style.SUCCESS('✅ MIGRACIÓN COMPLETADA'))
        self.stdout.write(self.style.SUCCESS('='*70))
        self.stdout.write('')
        
        if not dry_run:
            self.stdout.write(self.style.WARNING('⚠️  IMPORTANTE:'))
            self.stdout.write('Las contraseñas ahora están encriptadas.')
            self.stdout.write('Usa los métodos get_password() para obtenerlas en texto plano.')
            self.stdout.write('')
