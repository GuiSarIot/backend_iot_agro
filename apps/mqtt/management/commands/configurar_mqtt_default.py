"""
Management command para configurar MQTT por defecto
"""

from django.core.management.base import BaseCommand
from apps.mqtt.models import BrokerConfig, MQTTTopic


class Command(BaseCommand):
    help = 'Crea configuracion MQTT/EMQX por defecto'
    
    def handle(self, *args, **options):
        # Crear broker por defecto
        self.stdout.write('Creando broker por defecto...')
        
        broker, created = BrokerConfig.objects.get_or_create(
            nombre='EMQX Local',
            defaults={
                'host': 'localhost',
                'port': 1883,
                'protocol': 'mqtt',
                'username': 'admin',
                'password': 'public',
                'keepalive': 60,
                'clean_session': True,
                'use_tls': False,
                'is_active': True
            }
        )
        
        if created:
            self.stdout.write(
                self.style.SUCCESS(f'✓ Broker creado: {broker.nombre} ({broker.host}:{broker.port})')
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'- Broker ya existe: {broker.nombre}')
            )
        
        # Crear topics por defecto
        self.stdout.write('\nCreando topics por defecto...')
        
        topics_data = [
            {
                'nombre': 'Datos de Sensores',
                'topic_pattern': 'iot/sensors/{device_id}/data',
                'tipo': 'publish',
                'qos': 1,
                'retain': False,
                'descripcion': 'Topic para publicar datos de sensores'
            },
            {
                'nombre': 'Comandos a Dispositivos',
                'topic_pattern': 'iot/devices/{device_id}/commands',
                'tipo': 'subscribe',
                'qos': 1,
                'retain': False,
                'descripcion': 'Topic para recibir comandos en dispositivos'
            },
            {
                'nombre': 'Estado de Dispositivos',
                'topic_pattern': 'iot/devices/{device_id}/status',
                'tipo': 'both',
                'qos': 1,
                'retain': True,
                'descripcion': 'Topic para publicar y suscribirse al estado de dispositivos'
            },
            {
                'nombre': 'Alertas',
                'topic_pattern': 'iot/alerts/{device_id}',
                'tipo': 'publish',
                'qos': 2,
                'retain': False,
                'descripcion': 'Topic para publicar alertas criticas'
            },
        ]
        
        topics_created = 0
        for topic_data in topics_data:
            topic, created = MQTTTopic.objects.get_or_create(
                nombre=topic_data['nombre'],
                defaults={
                    'topic_pattern': topic_data['topic_pattern'],
                    'tipo': topic_data['tipo'],
                    'qos': topic_data['qos'],
                    'retain': topic_data['retain'],
                    'descripcion': topic_data['descripcion']
                }
            )
            
            if created:
                topics_created += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Topic creado: {topic.nombre} ({topic.topic_pattern})')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'- Topic ya existe: {topic.nombre}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Configuracion MQTT completada.\n'
                f'  Brokers creados: {1 if created else 0}\n'
                f'  Topics creados: {topics_created}'
            )
        )
