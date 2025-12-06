# 🔄 Sincronización Automática: Dispositivos ↔ Usuarios EMQX

## 📋 Resumen

Se ha implementado sincronización automática mediante **Django Signals** para que cada vez que se crea un dispositivo IoT, automáticamente se genere su usuario EMQX con credenciales únicas y reglas ACL predeterminadas.

## ✨ Características Implementadas

### 1. **Creación Automática de Usuarios EMQX**

Cuando creas un `Dispositivo` en el sistema:
```python
dispositivo = Dispositivo.objects.create(
    nombre="ESP32 Sensor Temperatura",
    tipo="esp32",
    identificador_unico="ESP32_TEMP_001",
    ubicacion="Sala Principal"
)
```

**Automáticamente se crea:**
- ✅ Usuario EMQX con username: `device_ESP32_TEMP_001`
- ✅ Contraseña aleatoria segura (24 caracteres)
- ✅ 5 reglas ACL predeterminadas
- ✅ Hash SHA256(password + salt) compatible con EMQX

### 2. **Reglas ACL Predeterminadas**

Cada dispositivo recibe automáticamente estas reglas:

| # | Permiso | Acción | Topic | QoS | Retain | Propósito |
|---|---------|--------|-------|-----|--------|-----------|
| 1 | allow | publish | `iot/sensors/{device_id}/#` | 1 | 0 | Publicar datos de sensores |
| 2 | allow | publish | `iot/devices/{device_id}/status` | 1 | 1 | Publicar estado (retenido) |
| 3 | allow | subscribe | `iot/commands/{device_id}/#` | 1 | - | Recibir comandos |
| 4 | allow | subscribe | `iot/config/{device_id}/#` | 1 | - | Recibir configuración |
| 5 | deny | all | `#` | - | - | Denegar todo lo demás |

### 3. **Eliminación en Cascada**

Al eliminar un dispositivo:
```python
dispositivo.delete()
```

**Automáticamente:**
- ✅ Se elimina el usuario EMQX asociado
- ✅ Se eliminan todas las reglas ACL (CASCADE)
- ✅ Se invalidan las credenciales MQTT

## 🎯 API Endpoints

### Consultar Credenciales MQTT de un Dispositivo

**Endpoint:** `GET /api/devices/{id}/mqtt-credentials/`

**Para usuarios normales:**
```json
{
  "has_mqtt_user": true,
  "mqtt_username": "device_ESP32_TEMP_001",
  "is_superuser": false,
  "created": "2025-12-05T10:30:00Z",
  "acl_rules_count": 5,
  "message": "Solo superusuarios pueden ver credenciales completas"
}
```

**Para superusuarios:**
```json
{
  "has_mqtt_user": true,
  "mqtt_username": "device_ESP32_TEMP_001",
  "is_superuser": false,
  "created": "2025-12-05T10:30:00Z",
  "acl_rules_count": 5,
  "password_hash": "a3f2...",
  "salt": "b8d4...",
  "acl_rules": [
    {
      "permission": "allow",
      "action": "publish",
      "topic": "iot/sensors/ESP32_TEMP_001/#",
      "qos": 1,
      "retain": 0
    },
    // ... más reglas
  ]
}
```

### Gestión de Usuarios EMQX

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/mqtt/emqx-users/` | Listar usuarios EMQX |
| POST | `/api/mqtt/emqx-users/` | Crear usuario manual |
| GET | `/api/mqtt/emqx-users/{id}/` | Detalle (incluye ACL) |
| PUT | `/api/mqtt/emqx-users/{id}/` | Actualizar usuario |
| DELETE | `/api/mqtt/emqx-users/{id}/` | Eliminar usuario |
| GET | `/api/mqtt/emqx-users/{id}/credentials/` | Ver credenciales (superusuarios) |
| POST | `/api/mqtt/emqx-users/{id}/change_password/` | Cambiar contraseña |
| POST | `/api/mqtt/emqx-users/create_with_acl/` | Crear con reglas ACL custom |

### Gestión de Reglas ACL

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/mqtt/emqx-acl/` | Listar reglas ACL |
| POST | `/api/mqtt/emqx-acl/` | Crear regla |
| GET | `/api/mqtt/emqx-acl/{id}/` | Detalle de regla |
| PUT | `/api/mqtt/emqx-acl/{id}/` | Actualizar regla |
| DELETE | `/api/mqtt/emqx-acl/{id}/` | Eliminar regla |
| GET | `/api/mqtt/emqx-acl/by_device/?dispositivo_id=X` | Reglas por dispositivo |

## 📝 Ejemplos de Uso

### Crear Dispositivo (Auto-genera Usuario EMQX)

```bash
# Via API
curl -X POST http://localhost:8000/api/devices/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Sensor Humedad Invernadero",
    "tipo": "esp32",
    "identificador_unico": "ESP32_HUM_INV_001",
    "ubicacion": "Invernadero Norte",
    "estado": "activo"
  }'

# Respuesta incluye el dispositivo creado
# En logs verás: "✓ Usuario EMQX creado para dispositivo..."
```

### Consultar Credenciales MQTT

```bash
# Obtener credenciales del dispositivo
curl -X GET http://localhost:8000/api/devices/1/mqtt-credentials/ \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Cambiar Contraseña MQTT de un Dispositivo

```bash
# Cambiar password del usuario EMQX
curl -X POST http://localhost:8000/api/mqtt/emqx-users/1/change_password/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"password": "nueva_password_segura_123"}'
```

### Agregar Regla ACL Custom

```bash
# Permitir al dispositivo publicar en un topic adicional
curl -X POST http://localhost:8000/api/mqtt/emqx-acl/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "device_ESP32_HUM_INV_001",
    "permission": "allow",
    "action": "publish",
    "topic": "iot/alerts/ESP32_HUM_INV_001",
    "qos": 2,
    "retain": 1
  }'
```

### Crear Usuario EMQX con ACL Custom (Manual)

```bash
curl -X POST http://localhost:8000/api/mqtt/emqx-users/create_with_acl/ \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "gateway_principal",
    "password": "gateway_password_secure",
    "is_superuser": false,
    "dispositivo_id": 5,
    "acl_rules": [
      {
        "permission": "allow",
        "action": "publish",
        "topic": "iot/sensors/+/#"
      },
      {
        "permission": "allow",
        "action": "subscribe",
        "topic": "iot/commands/gateway/#"
      }
    ]
  }'
```

## 🔐 Seguridad

### Contraseñas Generadas

- Longitud: 24 caracteres
- Método: `secrets.token_urlsafe(24)`
- Caracteres: URL-safe (A-Z, a-z, 0-9, _, -)
- **Ejemplo:** `xK9_vR2mP4wQ7nL5tJ8cYuN3`

### Hash en Base de Datos

```
password_hash = SHA256(password + salt)
salt = secrets.token_hex(16)  # 32 caracteres hex
```

### Logs de Auditoría

Todos los cambios quedan registrados:
```
[INFO] Usuario EMQX creado para dispositivo 'ESP32 Sensor Temperatura'
  Username: device_ESP32_TEMP_001
  Password: xK9_vR2mP4wQ7nL5tJ8cYuN3
  IMPORTANTE: Guarde estas credenciales de forma segura.

[INFO] ✓ Reglas ACL creadas para usuario EMQX 'device_ESP32_TEMP_001'
```

## 📂 Archivos Creados/Modificados

### Nuevos Archivos
- `apps/mqtt/signals.py` - Señales de sincronización automática
- `SINCRONIZACION_DISPOSITIVOS_EMQX.md` - Este archivo

### Archivos Modificados
- `apps/mqtt/apps.py` - Registro de señales
- `apps/mqtt/views.py` - ViewSets para EMQXUser y EMQXACL
- `apps/mqtt/urls.py` - URLs de nuevos endpoints
- `apps/devices/views.py` - Endpoint `mqtt_credentials`
- `.github/copilot-instructions.md` - Documentación actualizada

## 🧪 Testing

### Verificar Sincronización

```python
from apps.devices.models import Dispositivo
from apps.mqtt.models import EMQXUser, EMQXACL

# Crear dispositivo
device = Dispositivo.objects.create(
    nombre="Test Device",
    tipo="esp32",
    identificador_unico="TEST_001",
    ubicacion="Lab"
)

# Verificar usuario EMQX creado
emqx_user = EMQXUser.objects.get(dispositivo=device)
print(f"Username: {emqx_user.username}")  # device_TEST_001
print(f"ACL Rules: {emqx_user.acl_rules.count()}")  # 5

# Verificar reglas
for rule in emqx_user.acl_rules.all():
    print(f"{rule.permission} {rule.action} on {rule.topic}")

# Eliminar dispositivo (elimina usuario EMQX en cascada)
device.delete()
assert not EMQXUser.objects.filter(username="device_TEST_001").exists()
```

## 🚀 Próximos Pasos

1. **Ejecutar migraciones** (si aún no lo has hecho):
   ```bash
   python manage.py makemigrations mqtt
   python manage.py migrate mqtt
   ```

2. **Crear usuarios EMQX de prueba**:
   ```bash
   python manage.py crear_usuarios_emqx_default
   ```

3. **Crear un dispositivo de prueba**:
   ```bash
   python manage.py shell
   >>> from apps.devices.models import Dispositivo
   >>> d = Dispositivo.objects.create(
   ...     nombre="ESP32 Test",
   ...     tipo="esp32",
   ...     identificador_unico="ESP32_TEST_001",
   ...     ubicacion="Lab"
   ... )
   >>> # Verificar en logs la creación del usuario EMQX
   ```

4. **Configurar EMQX Dashboard** con las queries SQL de `EMQX_POSTGRESQL_INTEGRATION.md`

5. **Probar conexión MQTT** desde un dispositivo IoT con las credenciales generadas

## 📚 Referencias

- `EMQX_POSTGRESQL_INTEGRATION.md` - Guía completa de configuración EMQX
- `MQTT_INTEGRATION.md` - Patrones de topics y arquitectura MQTT
- `.github/copilot-instructions.md` - Instrucciones para agentes AI
