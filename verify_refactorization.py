#!/usr/bin/env python
"""
Script de verificación de la refactorización
Verifica que todos los componentes estén correctamente configurados
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.apps import apps
from django.db import connection

def test_apps():
    """Verificar que todas las apps estén instaladas"""
    print("\n=== Verificando Apps ===")
    required_apps = ['accounts', 'sensors', 'devices', 'readings', 'mqtt']
    
    for app_name in required_apps:
        app_config = apps.get_app_config(app_name)
        print(f"✓ App '{app_name}' instalada: {app_config.verbose_name}")
    
    return True

def test_models():
    """Verificar que todos los modelos existan"""
    print("\n=== Verificando Modelos ===")
    
    models_to_check = [
        ('accounts', 'CustomUser'),
        ('accounts', 'Rol'),
        ('accounts', 'Permiso'),
        ('sensors', 'Sensor'),
        ('devices', 'Dispositivo'),
        ('devices', 'DispositivoSensor'),
        ('readings', 'Lectura'),
        ('mqtt', 'BrokerConfig'),
        ('mqtt', 'MQTTCredential'),
        ('mqtt', 'MQTTTopic'),
        ('mqtt', 'DeviceMQTTConfig'),
    ]
    
    for app_label, model_name in models_to_check:
        try:
            model = apps.get_model(app_label, model_name)
            print(f"✓ Modelo {app_label}.{model_name} existe")
        except LookupError:
            print(f"✗ Modelo {app_label}.{model_name} NO ENCONTRADO")
            return False
    
    return True

def test_db_tables():
    """Verificar nombres de tablas personalizados"""
    print("\n=== Verificando Nombres de Tablas ===")
    
    expected_tables = {
        'users': 'accounts.CustomUser',
        'roles': 'accounts.Rol',
        'permisos': 'accounts.Permiso',
        'sensores': 'sensors.Sensor',
        'dispositivos': 'devices.Dispositivo',
        'dispositivos_sensores': 'devices.DispositivoSensor',
        'lecturas': 'readings.Lectura',
        'mqtt_broker_config': 'mqtt.BrokerConfig',
        'mqtt_credentials': 'mqtt.MQTTCredential',
        'mqtt_topics': 'mqtt.MQTTTopic',
        'mqtt_device_config': 'mqtt.DeviceMQTTConfig',
    }
    
    for table_name, model_path in expected_tables.items():
        app_label, model_name = model_path.split('.')
        model = apps.get_model(app_label, model_name)
        actual_table = model._meta.db_table
        
        if actual_table == table_name:
            print(f"✓ Tabla '{table_name}' correcta para {model_path}")
        else:
            print(f"✗ Tabla incorrecta: esperado '{table_name}', actual '{actual_table}'")
            return False
    
    return True

def test_mqtt_fields():
    """Verificar campos MQTT agregados"""
    print("\n=== Verificando Campos MQTT ===")
    
    # Verificar campos en Dispositivo
    Dispositivo = apps.get_model('devices', 'Dispositivo')
    mqtt_device_fields = ['mqtt_enabled', 'mqtt_client_id', 'last_seen', 'connection_status']
    
    for field_name in mqtt_device_fields:
        if hasattr(Dispositivo, field_name):
            print(f"✓ Dispositivo.{field_name} existe")
        else:
            print(f"✗ Dispositivo.{field_name} NO ENCONTRADO")
            return False
    
    # Verificar campos en Sensor
    Sensor = apps.get_model('sensors', 'Sensor')
    mqtt_sensor_fields = ['mqtt_topic_suffix', 'publish_interval']
    
    for field_name in mqtt_sensor_fields:
        if hasattr(Sensor, field_name):
            print(f"✓ Sensor.{field_name} existe")
        else:
            print(f"✗ Sensor.{field_name} NO ENCONTRADO")
            return False
    
    # Verificar campos en Lectura
    Lectura = apps.get_model('readings', 'Lectura')
    mqtt_reading_fields = ['mqtt_message_id', 'mqtt_qos', 'mqtt_retained']
    
    for field_name in mqtt_reading_fields:
        if hasattr(Lectura, field_name):
            print(f"✓ Lectura.{field_name} existe")
        else:
            print(f"✗ Lectura.{field_name} NO ENCONTRADO")
            return False
    
    return True

def test_management_commands():
    """Verificar comandos de gestión"""
    print("\n=== Verificando Management Commands ===")
    
    from django.core.management import get_commands
    commands = get_commands()
    
    required_commands = [
        'crear_permisos_default',
        'crear_roles_default',
        'crear_superuser',
        'configurar_mqtt_default',
    ]
    
    for cmd in required_commands:
        if cmd in commands:
            print(f"✓ Comando '{cmd}' disponible")
        else:
            print(f"✗ Comando '{cmd}' NO ENCONTRADO")
            return False
    
    return True

def main():
    """Ejecutar todas las verificaciones"""
    print("=" * 60)
    print("VERIFICACIÓN DE REFACTORIZACIÓN")
    print("=" * 60)
    
    tests = [
        ("Apps instaladas", test_apps),
        ("Modelos existentes", test_models),
        ("Nombres de tablas", test_db_tables),
        ("Campos MQTT", test_mqtt_fields),
        ("Management commands", test_management_commands),
    ]
    
    all_passed = True
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
            if not result:
                all_passed = False
        except Exception as e:
            print(f"\n✗ Error en prueba '{test_name}': {e}")
            results.append((test_name, False))
            all_passed = False
    
    # Resumen
    print("\n" + "=" * 60)
    print("RESUMEN DE VERIFICACIÓN")
    print("=" * 60)
    
    for test_name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {test_name}")
    
    print("=" * 60)
    
    if all_passed:
        print("\n✓✓✓ TODAS LAS VERIFICACIONES PASARON ✓✓✓")
        print("\nLa refactorización se completó exitosamente!")
        print("\nPróximos pasos:")
        print("1. Ejecutar migraciones: python manage.py migrate")
        print("2. Crear datos iniciales: python manage.py crear_superuser")
        print("3. Configurar MQTT: python manage.py configurar_mqtt_default")
        print("4. Iniciar servidor: python manage.py runserver")
        return 0
    else:
        print("\n✗✗✗ ALGUNAS VERIFICACIONES FALLARON ✗✗✗")
        print("\nRevisa los errores arriba y corrige los problemas.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
