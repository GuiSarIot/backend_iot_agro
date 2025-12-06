# 📚 API Documentation - IoT Sensor Platform

## Índice
1. [Autenticación](#autenticación)
2. [Usuarios](#usuarios)
3. [Roles y Permisos](#roles-y-permisos)
4. [Sensores](#sensores)
5. [Dispositivos](#dispositivos)
6. [Lecturas](#lecturas)
7. [Auditoría y Logs](#auditoría-y-logs)
8. [Notificaciones - Telegram](#notificaciones---telegram)
9. [Notificaciones - Email](#notificaciones---email)
10. [Dashboard](#dashboard)
11. [Códigos de Estado HTTP](#códigos-de-estado-http)
12. [Filtros y Búsqueda](#filtros-y-búsqueda)

---

## Autenticación

### 1. Registro de Usuario
**Endpoint**: `POST /api/auth/register/`  
**Permisos**: Público (AllowAny)

**Request Body**:
```json
{
  "username": "string",
  "email": "string",
  "password": "string",
  "password_confirm": "string",
  "first_name": "string",
  "last_name": "string",
  "tipo_usuario": "interno|externo",
  "rol": 1  // ID del rol (opcional)
}
```

**Response** (201 Created):
```json
{
  "user": {
    "id": 1,
    "username": "nuevo_usuario",
    "email": "usuario@example.com",
    "first_name": "Nombre",
    "last_name": "Apellido",
    "full_name": "Nombre Apellido",
    "tipo_usuario": "externo",
    "tipo_usuario_display": "Externo",
    "is_active": true,
    "rol": 2,
    "rol_detail": {...}
  },
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "message": "Usuario registrado exitosamente"
}
```

---

### 2. Login
**Endpoint**: `POST /api/auth/login/`  
**Permisos**: Público (AllowAny)

**Request Body**:
```json
{
  "username": "admin",
  "password": "admin123"
}
```

**Response** (200 OK):
```json
{
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@iotplatform.com",
    "full_name": "Super Admin",
    "tipo_usuario": "interno",
    "is_active": true,
    "is_superuser": true,
    "rol": 1,
    "rol_detail": {
      "id": 1,
      "nombre": "superusuario",
      "nombre_display": "Superusuario",
      "permisos": [...]
    }
  },
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "message": "Login exitoso"
}
```

---

### 3. Refresh Token
**Endpoint**: `POST /api/auth/refresh/`  
**Permisos**: Público (AllowAny)

**Request Body**:
```json
{
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response** (200 OK):
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

---

### 4. Cifrar ID de Usuario
**Endpoint**: `GET /api/login/cifrarID/{user_id}/`  
**Permisos**: Autenticado  
**Headers**: `Authorization: Bearer {access_token}`

**Response** (200 OK):
```json
{
  "encrypted_id": "1:1qaz2wsx3edc",
  "user_id": 1,
  "username": "admin"
}
```

---

### 5. Descifrar ID de Usuario
**Endpoint**: `POST /api/login/descifrarID/`  
**Permisos**: Autenticado  
**Headers**: `Authorization: Bearer {access_token}`

**Request Body**:
```json
{
  "encrypted_id": "1:1qaz2wsx3edc"
}
```

**Response** (200 OK):
```json
{
  "decrypted_id": 1,
  "user_id": 1,
  "username": "admin"
}
```

---

### 6. Perfil del Usuario Actual
**Endpoint**: `GET /api/users/me/`  
**Permisos**: Autenticado  
**Headers**: `Authorization: Bearer {access_token}`

**Response** (200 OK):
```json
{
  "id": 1,
  "username": "admin",
  "email": "admin@iotplatform.com",
  "first_name": "Super",
  "last_name": "Admin",
  "full_name": "Super Admin",
  "tipo_usuario": "interno",
  "tipo_usuario_display": "Interno",
  "is_active": true,
  "is_staff": true,
  "is_superuser": true,
  "rol": 1,
  "rol_detail": {...},
  "created_at": "2024-12-01T10:00:00Z",
  "updated_at": "2024-12-01T10:00:00Z",
  "last_login": "2024-12-04T08:30:00Z"
}
```

---

## Usuarios

### 1. Listar Usuarios
**Endpoint**: `GET /api/users/`  
**Permisos**: Superusuario  
**Headers**: `Authorization: Bearer {access_token}`

**Query Parameters**:
- `search`: Búsqueda por username, email, first_name, last_name
- `ordering`: Ordenar por username, created_at, last_login
- `page`: Número de página

**Response** (200 OK):
```json
{
  "count": 10,
  "next": "http://localhost:8000/api/users/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "username": "admin",
      "email": "admin@iotplatform.com",
      "full_name": "Super Admin",
      "tipo_usuario": "interno",
      "is_active": true,
      "rol": 1,
      "rol_detail": {...}
    }
  ]
}
```

---

### 2. Crear Usuario
**Endpoint**: `POST /api/users/`  
**Permisos**: Superusuario  
**Headers**: `Authorization: Bearer {access_token}`

**Request Body**:
```json
{
  "username": "operador1",
  "email": "operador1@example.com",
  "password": "password123",
  "first_name": "Operador",
  "last_name": "Uno",
  "tipo_usuario": "interno",
  "rol": 2,
  "is_active": true
}
```

**Response** (201 Created):
```json
{
  "id": 5,
  "username": "operador1",
  "email": "operador1@example.com",
  "first_name": "Operador",
  "last_name": "Uno",
  "tipo_usuario": "interno",
  "is_active": true,
  "rol": 2
}
```

---

### 3. Actualizar Usuario
**Endpoint**: `PUT/PATCH /api/users/{id}/`  
**Permisos**: Superusuario  
**Headers**: `Authorization: Bearer {access_token}`

**Request Body** (PATCH - parcial):
```json
{
  "is_active": false,
  "rol": 3
}
```

---

### 4. Activar Usuario
**Endpoint**: `POST /api/users/{id}/activate/`  
**Permisos**: Superusuario  
**Headers**: `Authorization: Bearer {access_token}`

**Response** (200 OK):
```json
{
  "message": "Usuario operador1 activado exitosamente"
}
```

---

### 5. Desactivar Usuario
**Endpoint**: `POST /api/users/{id}/deactivate/`  
**Permisos**: Superusuario  
**Headers**: `Authorization: Bearer {access_token}`

**Response** (200 OK):
```json
{
  "message": "Usuario operador1 desactivado exitosamente"
}
```

---

## Roles y Permisos

### 1. Listar Roles
**Endpoint**: `GET /api/roles/`  
**Permisos**: Superusuario

**Response** (200 OK):
```json
{
  "count": 3,
  "results": [
    {
      "id": 1,
      "nombre": "superusuario",
      "nombre_display": "Superusuario",
      "descripcion": "Tiene acceso completo a todas las funcionalidades del sistema",
      "permisos": [
        {
          "id": 1,
          "nombre": "Gestionar Usuarios",
          "codigo": "gestionar_usuarios",
          "descripcion": "Permite crear, editar y eliminar usuarios"
        }
      ],
      "created_at": "2024-12-01T10:00:00Z"
    }
  ]
}
```

---

### 2. Listar Permisos
**Endpoint**: `GET /api/permisos/`  
**Permisos**: Superusuario

**Response** (200 OK):
```json
{
  "count": 13,
  "results": [
    {
      "id": 1,
      "nombre": "Gestionar Usuarios",
      "codigo": "gestionar_usuarios",
      "descripcion": "Permite crear, editar y eliminar usuarios",
      "created_at": "2024-12-01T10:00:00Z"
    }
  ]
}
```

---

## Sensores

### 1. Listar Sensores
**Endpoint**: `GET /api/sensors/`  
**Permisos**: Autenticado  
**Headers**: `Authorization: Bearer {access_token}`

**Query Parameters**:
- `search`: Búsqueda por nombre, tipo, descripcion
- `tipo`: Filtrar por tipo de sensor
- `estado`: Filtrar por estado (activo, inactivo, mantenimiento)
- `ordering`: Ordenar por nombre, tipo, created_at

**Response** (200 OK):
```json
{
  "count": 6,
  "results": [
    {
      "id": 1,
      "nombre": "DHT22 - Temperatura",
      "tipo": "temperatura",
      "tipo_display": "Temperatura",
      "unidad_medida": "°C",
      "rango_min": -40.0,
      "rango_max": 80.0,
      "estado": "activo",
      "estado_display": "Activo",
      "descripcion": "",
      "created_by": 1,
      "created_by_username": "admin",
      "created_at": "2024-12-01T10:00:00Z",
      "updated_at": "2024-12-01T10:00:00Z"
    }
  ]
}
```

---

### 2. Crear Sensor
**Endpoint**: `POST /api/sensors/`  
**Permisos**: Superusuario o Operador  
**Headers**: `Authorization: Bearer {access_token}`

**Request Body**:
```json
{
  "nombre": "BMP280 - Presión",
  "tipo": "presion",
  "unidad_medida": "hPa",
  "rango_min": 300,
  "rango_max": 1100,
  "estado": "activo",
  "descripcion": "Sensor de presión barométrica"
}
```

**Response** (201 Created):
```json
{
  "id": 7,
  "nombre": "BMP280 - Presión",
  "tipo": "presion",
  "tipo_display": "Presión",
  "unidad_medida": "hPa",
  "rango_min": 300.0,
  "rango_max": 1100.0,
  "estado": "activo",
  "estado_display": "Activo",
  "created_by": 1,
  "created_by_username": "admin",
  "created_at": "2024-12-04T10:00:00Z"
}
```

---

### 3. Sensores Disponibles
**Endpoint**: `GET /api/sensors/available/`  
**Permisos**: Autenticado

**Response** (200 OK):
```json
[
  {
    "id": 1,
    "nombre": "DHT22 - Temperatura",
    "tipo": "temperatura",
    "estado": "activo",
    ...
  }
]
```

---

### 4. Tipos de Sensores
**Endpoint**: `GET /api/sensors/tipos/`  
**Permisos**: Autenticado

**Response** (200 OK):
```json
[
  {"value": "temperatura", "label": "Temperatura"},
  {"value": "humedad", "label": "Humedad"},
  {"value": "presion", "label": "Presión"},
  {"value": "luz", "label": "Luz"},
  {"value": "movimiento", "label": "Movimiento"},
  {"value": "gas", "label": "Gas"}
]
```

---

## Dispositivos

### 1. Listar Dispositivos
**Endpoint**: `GET /api/devices/`  
**Permisos**: Autenticado (Operadores ven solo sus dispositivos)  
**Headers**: `Authorization: Bearer {access_token}`

**Query Parameters**:
- `search`: Búsqueda por nombre, tipo, identificador_unico, ubicacion
- `tipo`: Filtrar por tipo de dispositivo
- `estado`: Filtrar por estado
- `operador`: Filtrar por ID de operador

**Response** (200 OK):
```json
{
  "count": 4,
  "results": [
    {
      "id": 1,
      "nombre": "Raspberry Pi - Sala",
      "tipo": "raspberry_pi",
      "tipo_display": "Raspberry Pi",
      "identificador_unico": "RPI-SALA-001",
      "ubicacion": "Sala Principal",
      "estado": "activo",
      "estado_display": "Activo",
      "descripcion": "",
      "operador_asignado": 2,
      "operador_username": "operador1",
      "sensores_asignados": [
        {
          "id": 1,
          "sensor": 1,
          "sensor_nombre": "DHT22 - Temperatura",
          "sensor_detail": {...},
          "configuracion_json": {},
          "activo": true,
          "fecha_asignacion": "2024-12-01T10:00:00Z"
        }
      ],
      "cantidad_sensores": 3,
      "created_at": "2024-12-01T10:00:00Z"
    }
  ]
}
```

---

### 2. Crear Dispositivo
**Endpoint**: `POST /api/devices/`  
**Permisos**: Superusuario o Operador  
**Headers**: `Authorization: Bearer {access_token}`

**Request Body**:
```json
{
  "nombre": "ESP32 - Oficina",
  "tipo": "esp32",
  "identificador_unico": "ESP32-OFICINA-001",
  "ubicacion": "Oficina Principal",
  "estado": "activo",
  "descripcion": "ESP32 en oficina con DHT22"
}
```

**Response** (201 Created):
```json
{
  "id": 5,
  "nombre": "ESP32 - Oficina",
  "tipo": "esp32",
  "tipo_display": "ESP32",
  "identificador_unico": "ESP32-OFICINA-001",
  "ubicacion": "Oficina Principal",
  "estado": "activo",
  "operador_asignado": null,
  "sensores_asignados": [],
  "cantidad_sensores": 0,
  "created_at": "2024-12-04T10:00:00Z"
}
```

---

### 3. Asignar Sensor a Dispositivo
**Endpoint**: `POST /api/devices/{id}/assign-sensor/`  
**Permisos**: Superusuario o Operador  
**Headers**: `Authorization: Bearer {access_token}`

**Request Body**:
```json
{
  "sensor_id": 1,
  "configuracion_json": {
    "intervalo": 60,
    "umbral_alerta": 30
  }
}
```

**Response** (201 Created):
```json
{
  "message": "Sensor asignado exitosamente",
  "asignacion": {
    "id": 10,
    "dispositivo": 5,
    "dispositivo_nombre": "ESP32 - Oficina",
    "sensor": 1,
    "sensor_nombre": "DHT22 - Temperatura",
    "configuracion_json": {
      "intervalo": 60,
      "umbral_alerta": 30
    },
    "activo": true,
    "fecha_asignacion": "2024-12-04T10:00:00Z"
  }
}
```

---

### 4. Asignar Operador a Dispositivo
**Endpoint**: `POST /api/devices/{id}/assign-operator/`  
**Permisos**: Superusuario  
**Headers**: `Authorization: Bearer {access_token}`

**Request Body**:
```json
{
  "operador_id": 2
}
```

**Response** (200 OK):
```json
{
  "message": "Operador asignado exitosamente",
  "dispositivo": {
    "id": 5,
    "nombre": "ESP32 - Oficina",
    "operador_asignado": 2,
    "operador_username": "operador1",
    ...
  }
}
```

---

### 5. Remover Sensor de Dispositivo
**Endpoint**: `DELETE /api/devices/{id}/remove-sensor/?sensor_id=1`  
**Permisos**: Superusuario o Operador  
**Headers**: `Authorization: Bearer {access_token}`

**Response** (200 OK):
```json
{
  "message": "Sensor removido exitosamente"
}
```

---

### 6. Tipos de Dispositivos
**Endpoint**: `GET /api/devices/tipos/`  
**Permisos**: Autenticado

**Response** (200 OK):
```json
[
  {"value": "raspberry_pi", "label": "Raspberry Pi"},
  {"value": "esp32", "label": "ESP32"},
  {"value": "arduino", "label": "Arduino"},
  {"value": "esp8266", "label": "ESP8266"}
]
```

---

## Lecturas

### 1. Listar Lecturas
**Endpoint**: `GET /api/readings/`  
**Permisos**: Autenticado (Operadores ven solo lecturas de sus dispositivos)  
**Headers**: `Authorization: Bearer {access_token}`

**Query Parameters**:
- `dispositivo`: Filtrar por ID de dispositivo
- `sensor`: Filtrar por ID de sensor
- `fecha_inicio`: Filtrar desde fecha (YYYY-MM-DDTHH:MM:SS)
- `fecha_fin`: Filtrar hasta fecha (YYYY-MM-DDTHH:MM:SS)
- `ordering`: Ordenar por timestamp

**Response** (200 OK):
```json
{
  "count": 120,
  "results": [
    {
      "id": 1,
      "dispositivo": 1,
      "dispositivo_nombre": "Raspberry Pi - Sala",
      "sensor": 1,
      "sensor_nombre": "DHT22 - Temperatura",
      "sensor_unidad": "°C",
      "valor": 25.5,
      "timestamp": "2024-12-04T10:30:00Z",
      "metadata_json": {}
    }
  ]
}
```

---

### 2. Crear Lectura
**Endpoint**: `POST /api/readings/`  
**Permisos**: Superusuario o Operador  
**Headers**: `Authorization: Bearer {access_token}`

**Request Body**:
```json
{
  "dispositivo": 1,
  "sensor": 1,
  "valor": 25.5,
  "metadata_json": {
    "calidad": "buena",
    "bateria": 85
  }
}
```

**Response** (201 Created):
```json
{
  "id": 121,
  "dispositivo": 1,
  "dispositivo_nombre": "Raspberry Pi - Sala",
  "sensor": 1,
  "sensor_nombre": "DHT22 - Temperatura",
  "sensor_unidad": "°C",
  "valor": 25.5,
  "timestamp": "2024-12-04T10:35:00Z",
  "metadata_json": {
    "calidad": "buena",
    "bateria": 85
  }
}
```

---

### 3. Crear Lecturas en Bulk
**Endpoint**: `POST /api/readings/bulk/`  
**Permisos**: Superusuario o Operador  
**Headers**: `Authorization: Bearer {access_token}`

**Request Body**:
```json
{
  "lecturas": [
    {
      "dispositivo": 1,
      "sensor": 1,
      "valor": 25.5
    },
    {
      "dispositivo": 1,
      "sensor": 2,
      "valor": 60.2
    },
    {
      "dispositivo": 2,
      "sensor": 3,
      "valor": 1013.25
    }
  ]
}
```

**Response** (201 Created):
```json
{
  "message": "3 lecturas creadas exitosamente",
  "count": 3
}
```

---

### 4. Estadísticas de Lecturas
**Endpoint**: `GET /api/readings/estadisticas/`  
**Permisos**: Autenticado  
**Headers**: `Authorization: Bearer {access_token}`

**Query Parameters**:
- `dispositivo`: ID de dispositivo
- `sensor`: ID de sensor

**Response** (200 OK):
```json
{
  "total": 120,
  "promedio": 24.8,
  "maximo": 32.5,
  "minimo": 18.2
}
```

---

## Auditoría y Logs

### 1. Listar Logs de Auditoría
**Endpoint**: `GET /api/audit-logs/`  
**Permisos**: Superusuario  
**Headers**: `Authorization: Bearer {access_token}`

**Filtros**:
- `action`: `CREATE`, `UPDATE`, `DELETE`
- `model_name`: Nombre del modelo
- `username`: Usuario que realizó la acción

**Response** (200 OK):
```json
{
  "count": 150,
  "next": "http://localhost:8000/api/audit-logs/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "timestamp": "2025-12-05T19:30:00Z",
      "user": 1,
      "username": "admin",
      "model_name": "Dispositivo",
      "object_id": "5",
      "object_repr": "Raspberry Pi 4 - Sensor Hub",
      "action": "UPDATE",
      "changes": {
        "estado": {"old": "offline", "new": "online"}
      },
      "ip_address": "192.168.1.100",
      "user_agent": "Mozilla/5.0..."
    }
  ]
}
```

---

### 2. Estadísticas de Auditoría
**Endpoint**: `GET /api/audit-logs/stats/`  
**Permisos**: Superusuario  
**Headers**: `Authorization: Bearer {access_token}`

**Response** (200 OK):
```json
{
  "total_logs": 150,
  "by_action": {
    "CREATE": 50,
    "UPDATE": 80,
    "DELETE": 20
  },
  "by_model": {
    "Dispositivo": 45,
    "Sensor": 38,
    "Lectura": 67
  },
  "recent_logs": [...]
}
```

---

### 3. Listar Logs de Acceso
**Endpoint**: `GET /api/access-logs/`  
**Permisos**: Autenticado (usuarios ven sus propios logs, superusuarios ven todos)  
**Headers**: `Authorization: Bearer {access_token}`

**Filtros**:
- `method`: `GET`, `POST`, `PUT`, `PATCH`, `DELETE`
- `status_code`: Código HTTP
- `module`: Módulo de la app

**Response** (200 OK):
```json
{
  "count": 500,
  "results": [
    {
      "id": 1,
      "timestamp": "2025-12-05T19:35:00Z",
      "user": 1,
      "username": "admin",
      "module": "devices",
      "endpoint": "/api/devices/",
      "method": "GET",
      "status_code": 200,
      "response_time_ms": 45.2,
      "ip_address": "192.168.1.100",
      "user_agent": "PostmanRuntime/7.32.0"
    }
  ]
}
```

---

### 4. Estadísticas de Acceso
**Endpoint**: `GET /api/access-logs/stats/`  
**Permisos**: Autenticado  
**Headers**: `Authorization: Bearer {access_token}`

**Response** (200 OK):
```json
{
  "total_requests": 500,
  "by_method": {
    "GET": 350,
    "POST": 100,
    "PUT": 30,
    "DELETE": 20
  },
  "by_status": {
    "200": 450,
    "201": 50,
    "400": 5,
    "404": 3
  },
  "avg_response_time_ms": 52.4
}
```

---

### 5. Crear Log de Acceso Manual
**Endpoint**: `POST /api/access-logs/create-log/`  
**Permisos**: Autenticado  
**Headers**: `Authorization: Bearer {access_token}`

**Request Body**:
```json
{
  "module": "custom",
  "endpoint": "/api/custom/action/",
  "method": "POST",
  "status_code": 200,
  "response_time_ms": 120.5
}
```

---

## Notificaciones - Telegram

### 1. Generar Código de Verificación
**Endpoint**: `POST /api/telegram/generate-verification/`  
**Permisos**: Autenticado  
**Headers**: `Authorization: Bearer {access_token}`

**Response** (200 OK):
```json
{
  "success": true,
  "verification_code": "A3F9B2C1",
  "expires_in_minutes": 15,
  "message": "Envía este código a @iot_sensor_platform_bot en Telegram"
}
```

---

### 2. Verificar Código (desde web)
**Endpoint**: `POST /api/telegram/verify-code/`  
**Permisos**: Autenticado  
**Headers**: `Authorization: Bearer {access_token}`

**Request Body**:
```json
{
  "code": "A3F9B2C1"
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Código verificado. Envíalo al bot de Telegram."
}
```

---

### 3. Vincular Cuenta (llamado por el bot)
**Endpoint**: `POST /api/telegram/link-account/`  
**Permisos**: Autenticado  
**Headers**: `Authorization: Bearer {access_token}`

**Request Body**:
```json
{
  "user_id": 1,
  "chat_id": "1393684739",
  "username": "usuario_telegram",
  "verification_code": "A3F9B2C1"
}
```

---

### 4. Desvincular Cuenta
**Endpoint**: `POST /api/telegram/unlink-account/`  
**Permisos**: Autenticado  
**Headers**: `Authorization: Bearer {access_token}`

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Cuenta de Telegram desvinculada"
}
```

---

### 5. Enviar Notificación (Superusuarios)
**Endpoint**: `POST /api/telegram/send-notification/`  
**Permisos**: Superusuario  
**Headers**: `Authorization: Bearer {access_token}`

**Request Body**:
```json
{
  "user_ids": [1, 2, 3],
  "message": "Mantenimiento programado para mañana",
  "notification_type": "warning",
  "send_to_all_verified": false
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Notificación enviada a 3 usuario(s)",
  "sent_to": [
    {"user_id": 1, "username": "admin", "chat_id": "123456789"}
  ]
}
```

---

### 6. Estado de Telegram
**Endpoint**: `GET /api/telegram/status/`  
**Permisos**: Autenticado  
**Headers**: `Authorization: Bearer {access_token}`

**Response** (200 OK):
```json
{
  "is_linked": true,
  "is_verified": true,
  "notifications_enabled": true,
  "can_receive_notifications": true,
  "telegram_username": "@usuario_telegram",
  "has_pending_verification": false
}
```

---

## Notificaciones - Email

### 1. Enviar Email de Verificación
**Endpoint**: `POST /api/email/send-verification/`  
**Permisos**: Autenticado  
**Headers**: `Authorization: Bearer {access_token}`

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Email de verificación enviado a usuario@example.com",
  "email": "usuario@example.com"
}
```

---

### 2. Verificar Token de Email
**Endpoint**: `GET /api/email/verify/?token=xyz123...`  
**Permisos**: Autenticado  
**Headers**: `Authorization: Bearer {access_token}`

**También acepta POST**:
```json
{
  "token": "xyz123..."
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Email verificado exitosamente",
  "email_verified": true
}
```

---

### 3. Actualizar Preferencias de Email
**Endpoint**: `POST /api/email/preferences/`  
**Permisos**: Autenticado  
**Headers**: `Authorization: Bearer {access_token}`

**Request Body**:
```json
{
  "email_notifications_enabled": true
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Preferencias actualizadas",
  "email_notifications_enabled": true,
  "can_receive_email_notifications": true
}
```

---

### 4. Enviar Notificación por Email (Superusuarios)
**Endpoint**: `POST /api/email/send-notification/`  
**Permisos**: Superusuario  
**Headers**: `Authorization: Bearer {access_token}`

**Request Body**:
```json
{
  "user_ids": [1, 2, 3],
  "message": "<h3>Mantenimiento</h3><p>El sistema estará en mantenimiento mañana</p>",
  "subject": "Mantenimiento del Sistema",
  "notification_type": "warning",
  "send_to_all_verified": false
}
```

**Response** (200 OK):
```json
{
  "success": true,
  "message": "Notificaciones enviadas: 3 exitosos, 0 fallidos",
  "results": {
    "sent": 3,
    "failed": 0,
    "errors": []
  }
}
```

---

### 5. Estado de Email
**Endpoint**: `GET /api/email/status/`  
**Permisos**: Autenticado  
**Headers**: `Authorization: Bearer {access_token}`

**Response** (200 OK):
```json
{
  "has_email": true,
  "email": "usuario@example.com",
  "is_verified": true,
  "notifications_enabled": true,
  "can_receive_notifications": true,
  "verification_sent_at": "2025-12-05T19:30:00Z",
  "has_pending_verification": false
}
```

---

## Dashboard

### 1. Estadísticas del Sistema
**Endpoint**: `GET /api/dashboard/stats/`  
**Permisos**: Autenticado  
**Headers**: `Authorization: Bearer {access_token}`

**Response para Superusuario** (200 OK):
```json
{
  "total_usuarios": 10,
  "total_sensores": 15,
  "sensores_activos": 12,
  "total_dispositivos": 8,
  "dispositivos_activos": 7,
  "total_lecturas": 1250
}
```

**Response para Operador** (200 OK):
```json
{
  "total_usuarios": 10,
  "total_sensores": 15,
  "sensores_activos": 12,
  "total_dispositivos": 8,
  "dispositivos_activos": 7,
  "total_lecturas": 1250,
  "mis_dispositivos": 2,
  "mis_lecturas": 380
}
```

---

## Códigos de Estado HTTP

| Código | Significado | Uso |
|--------|-------------|-----|
| 200 | OK | Petición exitosa |
| 201 | Created | Recurso creado exitosamente |
| 204 | No Content | Eliminación exitosa |
| 400 | Bad Request | Datos inválidos |
| 401 | Unauthorized | No autenticado |
| 403 | Forbidden | Sin permisos |
| 404 | Not Found | Recurso no encontrado |
| 500 | Internal Server Error | Error del servidor |

---

## Filtros y Búsqueda

### Búsqueda (search)
Disponible en endpoints de listado. Busca en múltiples campos.

Ejemplo:
```
GET /api/sensors/?search=temperatura
GET /api/users/?search=operador
```

### Ordenamiento (ordering)
Ordena los resultados por un campo específico. Usar `-` para orden descendente.

Ejemplo:
```
GET /api/readings/?ordering=-timestamp
GET /api/devices/?ordering=nombre
```

### Paginación
Todos los endpoints de listado soportan paginación.

Parámetros:
- `page`: Número de página
- `page_size`: Elementos por página (máx 50)

Ejemplo:
```
GET /api/sensors/?page=2&page_size=20
```

---

## Formato de Errores

### Error de Validación (400)
```json
{
  "campo": [
    "Este campo es requerido."
  ],
  "password": [
    "Las contraseñas no coinciden."
  ]
}
```

### Error de Autenticación (401)
```json
{
  "detail": "Las credenciales de autenticación no se proveyeron."
}
```

### Error de Permisos (403)
```json
{
  "detail": "No tiene permisos para realizar esta acción."
}
```

### Error no encontrado (404)
```json
{
  "detail": "No encontrado."
}
```

---

## Notas Importantes

1. **Autenticación**: Todos los endpoints (excepto register, login, refresh) requieren el header `Authorization: Bearer {access_token}`

2. **Tokens JWT**: 
   - Access token expira en 60 minutos
   - Refresh token expira en 24 horas

3. **Permisos por Rol**:
   - **Superusuario**: Acceso completo
   - **Operador**: Gestionar dispositivos asignados, sensores y lecturas
   - **Solo Lectura**: Solo visualización

4. **Validaciones**:
   - Los sensores tienen rangos min/max que se validan en las lecturas
   - Los dispositivos tienen identificadores únicos
   - Las lecturas validan que el sensor esté asignado al dispositivo

5. **Filtros de Operador**: Los operadores solo ven sus propios dispositivos y lecturas relacionadas

---

**Para más información, consulta la documentación interactiva en**: http://localhost:8000/api/docs/
