"""
Management command para crear permisos por defecto
"""

from django.core.management.base import BaseCommand
from apps.accounts.models import Permiso


class Command(BaseCommand):
    help = 'Crea los permisos por defecto del sistema'
    
    def handle(self, *args, **options):
        permisos = [
            {
                'nombre': 'Gestionar Usuarios',
                'codigo': 'gestionar_usuarios',
                'descripcion': 'Permite crear, editar y eliminar usuarios'
            },
            {
                'nombre': 'Ver Usuarios',
                'codigo': 'ver_usuarios',
                'descripcion': 'Permite ver la lista de usuarios'
            },
            {
                'nombre': 'Gestionar Roles',
                'codigo': 'gestionar_roles',
                'descripcion': 'Permite crear, editar y eliminar roles'
            },
            {
                'nombre': 'Gestionar Permisos',
                'codigo': 'gestionar_permisos',
                'descripcion': 'Permite crear, editar y eliminar permisos'
            },
            {
                'nombre': 'Gestionar Sensores',
                'codigo': 'gestionar_sensores',
                'descripcion': 'Permite crear, editar y eliminar sensores'
            },
            {
                'nombre': 'Ver Sensores',
                'codigo': 'ver_sensores',
                'descripcion': 'Permite ver la lista de sensores'
            },
            {
                'nombre': 'Gestionar Dispositivos',
                'codigo': 'gestionar_dispositivos',
                'descripcion': 'Permite crear, editar y eliminar dispositivos'
            },
            {
                'nombre': 'Ver Dispositivos',
                'codigo': 'ver_dispositivos',
                'descripcion': 'Permite ver la lista de dispositivos'
            },
            {
                'nombre': 'Asignar Sensores',
                'codigo': 'asignar_sensores',
                'descripcion': 'Permite asignar sensores a dispositivos'
            },
            {
                'nombre': 'Asignar Operadores',
                'codigo': 'asignar_operadores',
                'descripcion': 'Permite asignar operadores a dispositivos'
            },
            {
                'nombre': 'Crear Lecturas',
                'codigo': 'crear_lecturas',
                'descripcion': 'Permite crear lecturas de sensores'
            },
            {
                'nombre': 'Ver Lecturas',
                'codigo': 'ver_lecturas',
                'descripcion': 'Permite ver lecturas de sensores'
            },
            {
                'nombre': 'Ver Dashboard',
                'codigo': 'ver_dashboard',
                'descripcion': 'Permite ver el dashboard con estadisticas'
            },
            {
                'nombre': 'Gestionar MQTT',
                'codigo': 'gestionar_mqtt',
                'descripcion': 'Permite gestionar configuracion MQTT/EMQX'
            },
            {
                'nombre': 'Ver Credenciales MQTT',
                'codigo': 'ver_credenciales_mqtt',
                'descripcion': 'Permite ver credenciales MQTT de dispositivos'
            },
        ]
        
        created_count = 0
        for permiso_data in permisos:
            permiso, created = Permiso.objects.get_or_create(
                codigo=permiso_data['codigo'],
                defaults={
                    'nombre': permiso_data['nombre'],
                    'descripcion': permiso_data['descripcion']
                }
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Permiso creado: {permiso.nombre}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'- Permiso ya existe: {permiso.nombre}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\n✓ Proceso completado. {created_count} permisos creados.')
        )
