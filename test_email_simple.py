"""
Script simple para probar el envío de emails
Ejecutar: python test_email_simple.py
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.accounts.models import CustomUser
from apps.accounts.email_helper import email_notifier


def test_email():
    """Prueba el envío de emails"""
    print("="*60)
    print("🧪 TEST DE EMAIL - IoT Sensor Platform")
    print("="*60)
    
    # 1. Verificar configuración
    print("\n📋 Verificando configuración...")
    is_configured, message = email_notifier._check_configuration()
    
    if is_configured:
        print(f"✅ {message}")
    else:
        print(f"❌ {message}")
        print("\n⚠️  Configura las variables de email en .env:")
        print("   EMAIL_HOST_USER=tu_email@gmail.com")
        print("   EMAIL_HOST_PASSWORD=tu_contraseña_de_aplicacion")
        return
    
    # 2. Buscar usuario con email
    print("\n👤 Buscando usuario con email...")
    user = CustomUser.objects.filter(email__isnull=False).exclude(email='').first()
    
    if not user:
        print("❌ No hay usuarios con email configurado")
        print("\n💡 Crea un usuario con email o actualiza uno existente:")
        print("   python manage.py shell")
        print("   >>> from apps.accounts.models import CustomUser")
        print("   >>> user = CustomUser.objects.get(username='admin')")
        print("   >>> user.email = 'tu_email@gmail.com'")
        print("   >>> user.save()")
        return
    
    print(f"✅ Usuario encontrado: {user.username} ({user.email})")
    
    # 3. Enviar email de prueba
    print("\n📧 Enviando email de prueba...")
    
    success, data = email_notifier.send_notification_to_user(
        user=user,
        message="""
        <h2>🎉 ¡Email funcionando!</h2>
        <p>Este es un mensaje de prueba del sistema <strong>IoT Sensor Platform</strong>.</p>
        <p>Si recibes este email, significa que la configuración es correcta.</p>
        <hr>
        <p><small>Timestamp: {}</small></p>
        """.format(__import__('datetime').datetime.now()),
        notification_type='success',
        subject='✅ Test de Email - IoT Sensor Platform'
    )
    
    # 4. Mostrar resultado
    print("\n" + "-"*60)
    if success:
        print("✅ ¡Email enviado exitosamente!")
        print(f"   Destinatario: {data.get('recipient')}")
        print(f"\n📱 Revisa tu bandeja de entrada: {user.email}")
        print("   (Si no lo ves, revisa la carpeta de spam)")
    else:
        print("❌ Error al enviar email")
        print(f"   Error: {data.get('error')}")
        print("\n💡 Posibles soluciones:")
        print("   1. Verifica que EMAIL_HOST_USER y EMAIL_HOST_PASSWORD estén correctos")
        print("   2. Para Gmail, usa una contraseña de aplicación")
        print("   3. Verifica tu conexión a internet")
        print("   4. Revisa los logs del servidor")
    
    print("\n" + "="*60)


if __name__ == '__main__':
    try:
        test_email()
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        import traceback
        traceback.print_exc()
