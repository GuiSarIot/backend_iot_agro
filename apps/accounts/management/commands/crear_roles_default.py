"""
Management command para crear roles por defecto
"""

from django.core.management.base import BaseCommand
from apps.accounts.models import Rol, Permiso


class Command(BaseCommand):
    help = 'Crea los roles por defecto del sistema con sus permisos'
    
    def handle(self, *args, **options):
        # Primero crear los permisos si no existen
        self.stdout.write('Verificando permisos...')
        from django.core.management import call_command
        call_command('crear_permisos_default')
        
        # Definir roles y sus permisos
        roles_config = {
            'superusuario': {
                'descripcion': 'Tiene acceso completo a todas las funcionalidades del sistema',
                'permisos': [
                    'gestionar_usuarios', 'ver_usuarios',
                    'gestionar_roles', 'gestionar_permisos',
                    'gestionar_sensores', 'ver_sensores',
                    'gestionar_dispositivos', 'ver_dispositivos',
                    'asignar_sensores', 'asignar_operadores',
                    'crear_lecturas', 'ver_lecturas',
                    'ver_dashboard', 'gestionar_mqtt',
                    'ver_credenciales_mqtt'
                ]
            },
            'operador': {
                'descripcion': 'Puede gestionar dispositivos asignados, sensores y crear lecturas',
                'permisos': [
                    'ver_usuarios',
                    'ver_sensores', 'gestionar_sensores',
                    'ver_dispositivos', 'asignar_sensores',
                    'crear_lecturas', 'ver_lecturas',
                    'ver_dashboard', 'ver_credenciales_mqtt'
                ]
            },
            'solo_lectura': {
                'descripcion': 'Solo puede ver informacion, sin permisos de edicion',
                'permisos': [
                    'ver_usuarios',
                    'ver_sensores',
                    'ver_dispositivos',
                    'ver_lecturas',
                    'ver_dashboard'
                ]
            }
        }
        
        created_count = 0
        for nombre_rol, config in roles_config.items():
            rol, created = Rol.objects.get_or_create(
                nombre=nombre_rol,
                defaults={'descripcion': config['descripcion']}
            )
            
            # Asignar permisos
            permisos = Permiso.objects.filter(codigo__in=config['permisos'])
            rol.permisos.set(permisos)
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Rol creado: {rol.get_nombre_display()} '
                        f'({permisos.count()} permisos asignados)'
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'- Rol actualizado: {rol.get_nombre_display()} '
                        f'({permisos.count()} permisos asignados)'
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\n✓ Proceso completado. {created_count} roles creados.')
        )
