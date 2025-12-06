"""
Señales para sincronización automática entre Dispositivos y Usuarios EMQX
"""

from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
import logging
import secrets

from apps.devices.models import Dispositivo
from .models import EMQXUser, EMQXACL

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Dispositivo)
def create_emqx_user_for_device(sender, instance, created, **kwargs):
    """
    Crea automáticamente un usuario EMQX cuando se crea un nuevo dispositivo.
    
    El usuario EMQX permite que el dispositivo IoT se conecte al broker MQTT
    con sus propias credenciales únicas.
    """
    if created:
        # Generar username basado en el identificador único del dispositivo
        mqtt_username = f"device_{instance.identificador_unico}"
        
        # Verificar si ya existe un usuario EMQX para este dispositivo
        if EMQXUser.objects.filter(username=mqtt_username).exists():
            logger.warning(
                f"Usuario EMQX '{mqtt_username}' ya existe para dispositivo {instance.nombre}"
            )
            return
        
        try:
            # Generar contraseña segura aleatoria
            mqtt_password = secrets.token_urlsafe(24)
            
            # Crear usuario EMQX
            emqx_user = EMQXUser(
                username=mqtt_username,
                is_superuser=False,
                dispositivo=instance
            )
            emqx_user.set_password(mqtt_password)
            emqx_user.save()
            
            # Crear reglas ACL predeterminadas
            create_default_acl_rules(emqx_user, instance)
            
            logger.info(
                f"✓ Usuario EMQX creado para dispositivo '{instance.nombre}'\n"
                f"  Username: {mqtt_username}\n"
                f"  Password: {mqtt_password}\n"
                f"  IMPORTANTE: Guarde estas credenciales de forma segura."
            )
            
            # Actualizar campos MQTT del dispositivo si existen
            if hasattr(instance, 'mqtt_client_id'):
                instance.mqtt_client_id = mqtt_username
                instance.mqtt_enabled = True
                instance.save(update_fields=['mqtt_client_id', 'mqtt_enabled'])
            
        except Exception as e:
            logger.error(
                f"Error al crear usuario EMQX para dispositivo {instance.nombre}: {str(e)}"
            )


def create_default_acl_rules(emqx_user, dispositivo):
    """
    Crea reglas ACL predeterminadas para un dispositivo IoT.
    
    Reglas creadas:
    1. Permitir publicar en topics del propio dispositivo
    2. Permitir suscribirse a comandos del dispositivo
    3. Denegar acceso a topics de otros dispositivos
    """
    device_id = dispositivo.identificador_unico
    
    # Regla 1: Permitir publicar datos de sensores
    EMQXACL.objects.create(
        username=emqx_user.username,
        emqx_user=emqx_user,
        permission='allow',
        action='publish',
        topic=f'iot/sensors/{device_id}/#',
        qos=1,
        retain=0
    )
    
    # Regla 2: Permitir publicar estado del dispositivo
    EMQXACL.objects.create(
        username=emqx_user.username,
        emqx_user=emqx_user,
        permission='allow',
        action='publish',
        topic=f'iot/devices/{device_id}/status',
        qos=1,
        retain=1  # Retener último estado
    )
    
    # Regla 3: Permitir suscribirse a comandos
    EMQXACL.objects.create(
        username=emqx_user.username,
        emqx_user=emqx_user,
        permission='allow',
        action='subscribe',
        topic=f'iot/commands/{device_id}/#',
        qos=1
    )
    
    # Regla 4: Permitir suscribirse a configuración
    EMQXACL.objects.create(
        username=emqx_user.username,
        emqx_user=emqx_user,
        permission='allow',
        action='subscribe',
        topic=f'iot/config/{device_id}/#',
        qos=1
    )
    
    # Regla 5: Denegar todo lo demás (seguridad)
    EMQXACL.objects.create(
        username=emqx_user.username,
        emqx_user=emqx_user,
        permission='deny',
        action='all',
        topic='#'  # Wildcard para todos los topics
    )
    
    logger.info(f"✓ Reglas ACL creadas para usuario EMQX '{emqx_user.username}'")


@receiver(pre_delete, sender=Dispositivo)
def delete_emqx_user_for_device(sender, instance, **kwargs):
    """
    Elimina el usuario EMQX cuando se elimina un dispositivo.
    
    Esto asegura que las credenciales MQTT se invaliden automáticamente
    cuando un dispositivo es removido del sistema.
    """
    try:
        # Buscar usuario EMQX asociado
        emqx_user = EMQXUser.objects.filter(dispositivo=instance).first()
        
        if emqx_user:
            username = emqx_user.username
            # Las reglas ACL se eliminan automáticamente por CASCADE
            emqx_user.delete()
            logger.info(
                f"✓ Usuario EMQX '{username}' eliminado al borrar dispositivo '{instance.nombre}'"
            )
    except Exception as e:
        logger.error(
            f"Error al eliminar usuario EMQX para dispositivo {instance.nombre}: {str(e)}"
        )


@receiver(post_save, sender=EMQXUser)
def log_emqx_user_changes(sender, instance, created, **kwargs):
    """
    Registra cambios en usuarios EMQX para auditoría
    """
    if created:
        action = "creado"
    else:
        action = "actualizado"
    
    device_info = f" para dispositivo '{instance.dispositivo.nombre}'" if instance.dispositivo else ""
    logger.info(f"Usuario EMQX '{instance.username}' {action}{device_info}")


@receiver(post_save, sender=EMQXACL)
def log_acl_changes(sender, instance, created, **kwargs):
    """
    Registra cambios en reglas ACL para auditoría
    """
    if created:
        logger.info(
            f"Regla ACL creada: {instance.username} - "
            f"{instance.permission} {instance.action} on '{instance.topic}'"
        )
