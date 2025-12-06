# Integración EMQX con PostgreSQL - Guía de Configuración

## Resumen

Este proyecto incluye modelos compatibles con el esquema de autenticación y autorización de EMQX usando PostgreSQL como backend. Los modelos `EMQXUser` y `EMQXACL` permiten gestionar usuarios MQTT y sus permisos directamente desde Django.

## Arquitectura

```
┌─────────────────┐         ┌──────────────┐         ┌─────────────────┐
│  Dispositivos   │◄───────►│  EMQX Broker │◄───────►│   PostgreSQL    │
│  IoT (ESP32,    │  MQTT   │              │  SQL    │   (Django DB)   │
│  Raspberry Pi)  │         │  Auth/Authz  │         │  mqtt_user      │
└─────────────────┘         └──────────────┘         │  mqtt_acl       │
                                                      └─────────────────┘
```

## Modelos

### EMQXUser (Tabla: `mqtt_user`)

Gestiona la autenticación de usuarios MQTT en EMQX.

**Campos:**
- `username`: Nombre de usuario único para MQTT
- `password_hash`: Hash SHA256 de la contraseña
- `salt`: Salt aleatorio para el hash
- `is_superuser`: Si es true, tiene acceso completo sin restricciones ACL
- `dispositivo`: Relación opcional con un dispositivo IoT
- `created`: Fecha de creación

**Métodos importantes:**
```python
# Crear usuario con contraseña hasheada
user = EMQXUser(username='device123')
user.set_password('mi_password_seguro')
user.save()

# Verificar contraseña
if user.verify_password('mi_password_seguro'):
    print("Password correcto!")
```

**Fórmula de hash:** `password_hash = SHA256(password + salt)`

### EMQXACL (Tabla: `mqtt_acl`)

Define reglas de autorización para publicación/suscripción en topics MQTT.

**Campos:**
- `username`: Usuario al que aplica la regla
- `permission`: `allow` o `deny`
- `action`: `publish`, `subscribe` o `all`
- `topic`: Patrón del topic MQTT (soporta wildcards)
- `qos`: Quality of Service (0, 1, 2, o NULL para todos)
- `retain`: Control de mensajes retenidos (0, 1, o NULL)
- `emqx_user`: Relación FK con EMQXUser (ayuda a mantener consistencia)

**Wildcards en topics:**
- `+`: Coincide con un solo nivel (ej: `iot/sensors/+/data`)
- `#`: Coincide con múltiples niveles (ej: `iot/sensors/#`)

**Ejemplo de reglas ACL:**
```python
# Permitir a 'device123' publicar en sus propios topics
EMQXACL.objects.create(
    username='device123',
    permission='allow',
    action='publish',
    topic='iot/sensors/device123/#',
    qos=1
)

# Permitir suscripción a comandos
EMQXACL.objects.create(
    username='device123',
    permission='allow',
    action='subscribe',
    topic='iot/commands/device123/#',
    qos=1
)

# Denegar publicación en topics de otros dispositivos
EMQXACL.objects.create(
    username='device123',
    permission='deny',
    action='publish',
    topic='iot/sensors/+/#',  # Todos los dispositivos
    qos=None  # Todos los QoS
)
```

## Configuración en EMQX

### 1. Configurar Autenticación PostgreSQL

1. Acceder al EMQX Dashboard: `http://localhost:18083` (user: admin, pass: public)
2. Ir a **Authentication** > **Create**
3. Seleccionar **PostgreSQL** como backend
4. Configurar conexión:
   ```
   Server: localhost:5432
   Database: iot_sensor_db
   Username: iot_user
   Password: iot_password_123
   ```
5. Configurar hash de contraseña:
   - **Password Hash**: SHA256
   - **Salt Position**: suffix
   - **SQL Query**:
   ```sql
   SELECT password_hash AS password_hash, salt, is_superuser 
   FROM mqtt_user 
   WHERE username = ${username} LIMIT 1
   ```

### 2. Configurar Autorización PostgreSQL

1. Ir a **Authorization** > **Create**
2. Seleccionar **PostgreSQL** como backend
3. Usar la misma configuración de conexión
4. **SQL Query**:
   ```sql
   SELECT permission, action, topic, qos, retain 
   FROM mqtt_acl 
   WHERE username = ${username}
   ```

### 3. Orden de Evaluación

EMQX evalúa las reglas ACL en orden:
1. Si `is_superuser = true`, se permite todo (sin consultar ACL)
2. Se cargan todas las reglas ACL del usuario
3. Se evalúan en orden hasta encontrar coincidencia
4. Primera regla que coincide determina el resultado (`allow` o `deny`)
5. Si no hay coincidencias, se deniega por defecto

## Gestión desde Django

### Management Command

Crear usuarios y reglas por defecto:
```bash
python manage.py crear_usuarios_emqx_default
```

Esto crea:
- **emqx_admin**: Superusuario EMQX (password: emqx_admin_password_123)
- **test_device**: Usuario de prueba con reglas ACL

### API Endpoints

Los nuevos modelos están disponibles a través de la API REST:

```
POST   /api/mqtt/emqx-users/              # Crear usuario EMQX
GET    /api/mqtt/emqx-users/              # Listar usuarios
GET    /api/mqtt/emqx-users/{id}/         # Detalle usuario (incluye ACL)
PUT    /api/mqtt/emqx-users/{id}/         # Actualizar usuario
DELETE /api/mqtt/emqx-users/{id}/         # Eliminar usuario

POST   /api/mqtt/emqx-acl/                # Crear regla ACL
GET    /api/mqtt/emqx-acl/                # Listar reglas
PUT    /api/mqtt/emqx-acl/{id}/           # Actualizar regla
DELETE /api/mqtt/emqx-acl/{id}/           # Eliminar regla

POST   /api/mqtt/emqx-users/create-with-acl/  # Crear usuario + ACL en una operación
```

### Crear Usuario desde API

```json
POST /api/mqtt/emqx-users/create-with-acl/
{
  "username": "sensor_esp32_001",
  "password": "secure_password_123",
  "is_superuser": false,
  "dispositivo": 1,
  "acl_rules": [
    {
      "permission": "allow",
      "action": "publish",
      "topic": "iot/sensors/esp32_001/#",
      "qos": 1
    },
    {
      "permission": "allow",
      "action": "subscribe",
      "topic": "iot/commands/esp32_001/#",
      "qos": 1
    }
  ]
}
```

### Admin Django

Los modelos están registrados en el Django Admin con interfaces amigables:
- **EMQXUser Admin**: Incluye inline de reglas ACL
- **EMQXACL Admin**: Con autocomplete para selección de usuario

## Patrones de Topics Recomendados

### Para Dispositivos IoT

```
iot/sensors/{device_id}/data              # Datos de sensores (publish)
iot/sensors/{device_id}/status            # Estado del dispositivo (publish)
iot/commands/{device_id}/#                # Comandos al dispositivo (subscribe)
iot/config/{device_id}/#                  # Configuración (subscribe)
```

### Reglas ACL Típicas

**Dispositivo estándar:**
```python
# Publicar en sus propios topics
topic='iot/sensors/{device_id}/#'
action='publish'

# Suscribirse a comandos
topic='iot/commands/{device_id}/#'
action='subscribe'
```

**Gateway/Agregador:**
```python
# Publicar múltiples dispositivos
topic='iot/sensors/+/#'
action='publish'

# Suscribirse a respuestas
topic='iot/responses/gateway_id/#'
action='subscribe'
```

## Seguridad

### Buenas Prácticas

1. **No usar superusuarios para dispositivos**: Crear usuarios específicos con ACL restrictivas
2. **Contraseñas fuertes**: Mínimo 12 caracteres, usar `secrets.token_urlsafe()`
3. **Topics específicos**: Evitar wildcards amplios como `#` en permissions
4. **Rotar credenciales**: Implementar rotación periódica de passwords
5. **Monitorear accesos**: Registrar intentos de autenticación fallidos

### Ejemplo de Usuario Restringido

```python
from apps.mqtt.models import EMQXUser, EMQXACL

# Crear usuario con acceso muy limitado
user = EMQXUser(username='sensor_temp_001', is_superuser=False)
user.set_password('temp_sensor_secure_pwd_xyz')
user.save()

# Solo puede publicar temperatura en su topic
EMQXACL.objects.create(
    username='sensor_temp_001',
    emqx_user=user,
    permission='allow',
    action='publish',
    topic='iot/sensors/temp_001/temperature',
    qos=1,
    retain=0
)

# Denegar todo lo demás explícitamente
EMQXACL.objects.create(
    username='sensor_temp_001',
    emqx_user=user,
    permission='deny',
    action='all',
    topic='#'
)
```

## Testing

### Verificar Configuración EMQX

Usar MQTTX o mosquitto_pub/sub para probar:

```bash
# Publicar con usuario autenticado
mosquitto_pub -h localhost -p 1883 \
  -u sensor_esp32_001 -P secure_password_123 \
  -t iot/sensors/esp32_001/data \
  -m '{"temperature": 25.5, "humidity": 60}'

# Suscribirse
mosquitto_sub -h localhost -p 1883 \
  -u sensor_esp32_001 -P secure_password_123 \
  -t iot/commands/esp32_001/#
```

### Verificar en Base de Datos

```sql
-- Ver usuarios EMQX
SELECT username, is_superuser, created FROM mqtt_user;

-- Ver reglas ACL de un usuario
SELECT username, permission, action, topic, qos 
FROM mqtt_acl 
WHERE username = 'sensor_esp32_001';
```

## Migración

Para aplicar los nuevos modelos:

```bash
python manage.py makemigrations mqtt
python manage.py migrate mqtt
python manage.py crear_usuarios_emqx_default
```

## Referencias

- [EMQX PostgreSQL Authentication](https://www.emqx.io/docs/en/latest/access-control/authn/postgresql.html)
- [EMQX PostgreSQL Authorization](https://www.emqx.io/docs/en/latest/access-control/authz/postgresql.html)
- [MQTT Topic Wildcards](https://www.emqx.io/docs/en/latest/messaging/mqtt-wildcards.html)
