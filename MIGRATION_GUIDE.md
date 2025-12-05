# Guía de Migración - Refactorización Backend

## Resumen de Cambios

Esta refactorización modulariza completamente el backend Django, separándolo en 5 apps especializadas:

- **accounts**: Gestión de usuarios, roles y permisos
- **sensors**: Gestión de sensores IoT
- **devices**: Gestión de dispositivos IoT
- **readings**: Registro y consulta de lecturas
- **mqtt**: Configuración MQTT/EMQX (NUEVO)

## Cambios en la Base de Datos

### Tablas Renombradas (eliminado prefijo "api_")

| Tabla Antigua | Tabla Nueva |
|--------------|-------------|
| api_customuser | users |
| api_rol | roles |
| api_permiso | permisos |
| api_sensor | sensores |
| api_dispositivo | dispositivos |
| api_dispositivosensor | dispositivos_sensores |
| api_lectura | lecturas |

### Nuevas Tablas MQTT

- mqtt_broker_config
- mqtt_credentials
- mqtt_topics
- mqtt_device_config

## Opciones de Migración

### Opción 1: Base de Datos Nueva (Recomendado para Desarrollo)

```bash
# 1. Eliminar base de datos existente
docker-compose down -v

# 2. Iniciar con la nueva estructura
docker-compose up -d

# Las migraciones se ejecutarán automáticamente
```

### Opción 2: Migración con Datos Existentes

Si tienes datos importantes que necesitas conservar:

```bash
# 1. Hacer backup de la base de datos
docker exec iot_sensor_platform-postgres-1 pg_dump -U iot_user iot_sensor_db > backup.sql

# 2. Aplicar migraciones
docker-compose exec backend python manage.py migrate

# 3. Las tablas antiguas se renombrarán automáticamente
# Los datos se preservarán
```

## Verificación Post-Migración

```bash
# Verificar migraciones
docker-compose exec backend python manage.py showmigrations

# Verificar configuración
docker-compose exec backend python manage.py check

# Crear datos de prueba
docker-compose exec backend python manage.py crear_superuser
docker-compose exec backend python manage.py configurar_mqtt_default
```

## Endpoints Actualizados

La estructura de endpoints se mantiene compatible:

- ✅ `/api/auth/` - Autenticación
- ✅ `/api/users/` - Usuarios
- ✅ `/api/sensors/` - Sensores
- ✅ `/api/devices/` - Dispositivos
- ✅ `/api/readings/` - Lecturas
- 🆕 `/api/mqtt/` - Configuración MQTT (NUEVO)

### Nuevos Endpoints MQTT

```
GET/POST   /api/mqtt/brokers/           - Gestión de brokers MQTT
GET/POST   /api/mqtt/credentials/       - Credenciales MQTT por dispositivo
GET/POST   /api/mqtt/topics/            - Topics MQTT
GET/POST   /api/mqtt/device-config/     - Configuración MQTT de dispositivos
POST       /api/mqtt/test-connection/   - Probar conexión al broker
GET        /api/mqtt/device-status/     - Estado de dispositivos MQTT
```

## Nuevos Campos en Modelos

### Dispositivo
- `mqtt_enabled` - Indica si MQTT está habilitado
- `mqtt_client_id` - Client ID MQTT único
- `last_seen` - Última vez que se conectó
- `connection_status` - Estado de conexión (online/offline/error)

### Sensor
- `mqtt_topic_suffix` - Sufijo del topic MQTT
- `publish_interval` - Intervalo de publicación recomendado

### Lectura
- `mqtt_message_id` - ID del mensaje MQTT
- `mqtt_qos` - Quality of Service
- `mqtt_retained` - Si el mensaje fue retenido

## Nuevos Permisos

- `gestionar_mqtt` - Gestionar configuración MQTT
- `ver_credenciales_mqtt` - Ver credenciales MQTT

## Comandos de Gestión Actualizados

```bash
# Crear permisos
python manage.py crear_permisos_default

# Crear roles
python manage.py crear_roles_default

# Crear superusuario
python manage.py crear_superuser

# Configurar MQTT (NUEVO)
python manage.py configurar_mqtt_default
```

## Credenciales por Defecto

### Superusuario
- Username: `admin`
- Password: `admin123`
- Email: `admin@iotsensor.com`

### Broker MQTT por Defecto
- Host: `localhost`
- Port: `1883`
- Username: `admin`
- Password: `public`

## Solución de Problemas

### Error: "No module named 'api'"

Si ves este error, asegúrate de que `api` esté comentado en `INSTALLED_APPS`:

```python
# config/settings.py
INSTALLED_APPS = [
    ...
    'apps.accounts',
    'apps.sensors',
    'apps.devices',
    'apps.readings',
    'apps.mqtt',
    # 'api',  # <-- Comentado
]
```

### Error: "Table already exists"

Si las tablas ya existen con el prefijo `api_`, necesitas renombrarlas:

```sql
-- Conectar a PostgreSQL
ALTER TABLE api_customuser RENAME TO users;
ALTER TABLE api_rol RENAME TO roles;
ALTER TABLE api_permiso RENAME TO permisos;
ALTER TABLE api_sensor RENAME TO sensores;
ALTER TABLE api_dispositivo RENAME TO dispositivos;
ALTER TABLE api_dispositivosensor RENAME TO dispositivos_sensores;
ALTER TABLE api_lectura RENAME TO lecturas;
```

## Rollback (si es necesario)

```bash
# 1. Restaurar backup
docker exec -i iot_sensor_platform-postgres-1 psql -U iot_user iot_sensor_db < backup.sql

# 2. Revertir código (checkout commit anterior)
git checkout <commit-anterior>

# 3. Reiniciar servicios
docker-compose restart
```

## Soporte

Para más información consulta:
- README.md - Guía de instalación y uso
- API_DOCUMENTATION.md - Documentación de endpoints
- MQTT_INTEGRATION.md - Guía de integración MQTT/EMQX
