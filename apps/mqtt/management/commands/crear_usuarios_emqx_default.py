"""
Management command para crear usuarios y reglas ACL por defecto en EMQX
"""

from django.core.management.base import BaseCommand
from apps.mqtt.models import EMQXUser, EMQXACL


class Command(BaseCommand):
    help = 'Crea usuarios EMQX y reglas ACL por defecto para integración con EMQX broker'
    
    def handle(self, *args, **options):
        self.stdout.write(
            self.style.WARNING('\n=== Creando Usuarios EMQX por Defecto ===\n')
        )
        
        # 1. Crear superusuario EMQX
        admin_user, created = EMQXUser.objects.get_or_create(
            username='emqx_admin',
            defaults={
                'is_superuser': True,
            }
        )
        
        if created:
            admin_user.set_password('emqx_admin_password_123')
            admin_user.save()
            self.stdout.write(
                self.style.SUCCESS(
                    f'✓ Superusuario EMQX creado:\n'
                    f'  Username: {admin_user.username}\n'
                    f'  Password: emqx_admin_password_123\n'
                    f'  Es Superusuario: {admin_user.is_superuser}'
                )
            )
        else:
            self.stdout.write(
                self.style.WARNING(f'- El superusuario "{admin_user.username}" ya existe.')
            )
        
        # 2. Crear usuario de prueba estándar
        test_user, created = EMQXUser.objects.get_or_create(
            username='test_device',
            defaults={
                'is_superuser': False,
            }
        )
        
        if created:
            test_user.set_password('test_password_123')
            test_user.save()
            self.stdout.write(
                self.style.SUCCESS(
                    f'\n✓ Usuario de prueba creado:\n'
                    f'  Username: {test_user.username}\n'
                    f'  Password: test_password_123\n'
                    f'  Es Superusuario: {test_user.is_superuser}'
                )
            )
            
            # Crear reglas ACL para usuario de prueba
            acl_rules = [
                {
                    'username': test_user.username,
                    'permission': 'allow',
                    'action': 'publish',
                    'topic': 'iot/sensors/test_device/#',
                    'qos': 1,
                    'emqx_user': test_user
                },
                {
                    'username': test_user.username,
                    'permission': 'allow',
                    'action': 'subscribe',
                    'topic': 'iot/commands/test_device/#',
                    'qos': 1,
                    'emqx_user': test_user
                },
            ]
            
            for rule_data in acl_rules:
                rule, rule_created = EMQXACL.objects.get_or_create(
                    username=rule_data['username'],
                    action=rule_data['action'],
                    topic=rule_data['topic'],
                    defaults=rule_data
                )
                if rule_created:
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'  ✓ ACL: {rule.permission} {rule.action} on {rule.topic}'
                        )
                    )
        else:
            self.stdout.write(
                self.style.WARNING(f'\n- El usuario de prueba "{test_user.username}" ya existe.')
            )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n{"="*60}\n'
                f'Configuración EMQX completada!\n\n'
                f'Para configurar EMQX PostgreSQL Authentication:\n'
                f'1. En EMQX Dashboard: Authentication > Create\n'
                f'2. Seleccionar "PostgreSQL" como backend\n'
                f'3. Configurar conexión a esta base de datos\n'
                f'4. Password Hash: SHA256\n'
                f'5. Salt Position: suffix\n'
                f'6. Query SQL:\n'
                f'   SELECT password_hash, salt, is_superuser\n'
                f'   FROM mqtt_user WHERE username = $1\n\n'
                f'Para configurar EMQX PostgreSQL Authorization:\n'
                f'1. En EMQX Dashboard: Authorization > Create\n'
                f'2. Seleccionar "PostgreSQL" como backend\n'
                f'3. Query SQL:\n'
                f'   SELECT permission, action, topic, qos, retain\n'
                f'   FROM mqtt_acl WHERE username = $1\n'
                f'{"="*60}\n'
            )
        )
