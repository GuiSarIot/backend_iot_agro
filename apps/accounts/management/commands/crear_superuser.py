"""
Management command para crear un superusuario por defecto
"""

from django.core.management.base import BaseCommand
from apps.accounts.models import CustomUser, Rol


class Command(BaseCommand):
    help = 'Crea un superusuario por defecto del sistema'
    
    def handle(self, *args, **options):
        # Crear roles primero
        from django.core.management import call_command
        call_command('crear_roles_default')
        
        username = 'admin'
        email = 'admin@iotsensor.com'
        password = 'admin123'
        
        if CustomUser.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.WARNING(f'- El superusuario "{username}" ya existe.')
            )
            return
        
        # Obtener rol de superusuario
        try:
            rol_superusuario = Rol.objects.get(nombre='superusuario')
        except Rol.DoesNotExist:
            rol_superusuario = None
        
        # Crear superusuario
        user = CustomUser.objects.create_superuser(
            username=username,
            email=email,
            password=password,
            first_name='Super',
            last_name='Admin',
            tipo_usuario='interno',
            rol=rol_superusuario
        )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'\n✓ Superusuario creado exitosamente:\n'
                f'  Username: {username}\n'
                f'  Email: {email}\n'
                f'  Password: {password}\n'
                f'  Rol: {user.rol.get_nombre_display() if user.rol else "N/A"}'
            )
        )
