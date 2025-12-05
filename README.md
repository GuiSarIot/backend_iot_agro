# 🌐 IoT Sensor Platform - Backend Django REST Framework

## 📋 Descripción

Plataforma backend completa para la gestión de sensores y dispositivos IoT desarrollada con Django REST Framework. Este sistema permite administrar sensores, dispositivos (Raspberry Pi, ESP32, Arduino), usuarios con diferentes roles y permisos, y registro de lecturas en tiempo real.

**Fase 1 del proyecto** - Backend completo con API REST

### ✨ Características Principales

- 🔐 **Autenticación JWT** con tokens de acceso y refresh
- 👥 **Sistema de roles y permisos** granular (Superusuario, Operador, Solo Lectura)
- 📊 **Gestión completa de sensores** (temperatura, humedad, presión, etc.)
- 🖥️ **Gestión de dispositivos IoT** (Raspberry Pi, ESP32, Arduino, etc.)
- 📈 **Registro y consulta de lecturas** de sensores
- 🔗 **Asignación de sensores a dispositivos** y **operadores a dispositivos**
- 📚 **Documentación automática de API** con Swagger/ReDoc
- 🐘 **Base de datos PostgreSQL**
- 🐳 **Dockerizado** para fácil despliegue
- 🔌 **Preparado para integración EMQX** (Fase 3)

---

## 🚀 Requisitos Previos

### Sin Docker:
- Python 3.11+
- PostgreSQL 15+
- pip

### Con Docker:
- Docker 20.10+
- Docker Compose 2.0+

---

## 📦 Instalación

### Opción 1: Instalación con Docker (Recomendado)

1. **Clonar el repositorio** (o navegar al directorio):
```bash
cd /home/ubuntu/iot_sensor_platform
```

2. **Copiar el archivo de variables de entorno**:
```bash
cp .env.example .env
```

3. **Editar el archivo .env** (opcional, los valores por defecto funcionan):
```bash
nano .env
```

4. **Construir y levantar los contenedores**:
```bash
docker-compose up --build
```

5. **Crear superusuario** (en otra terminal):
```bash
docker-compose exec django python manage.py crear_superuser
```

✅ **La API estará disponible en**: http://localhost:8000/api/

---

### Opción 2: Instalación sin Docker

1. **Crear entorno virtual**:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

2. **Instalar dependencias**:
```bash
pip install -r requirements.txt
```

3. **Configurar PostgreSQL**:
```sql
CREATE DATABASE iot_sensor_db;
CREATE USER iot_user WITH PASSWORD 'iot_password_123';
GRANT ALL PRIVILEGES ON DATABASE iot_sensor_db TO iot_user;
```

4. **Copiar y configurar variables de entorno**:
```bash
cp .env.example .env
# Editar .env con los datos de tu base de datos
nano .env
```

5. **Ejecutar migraciones**:
```bash
python manage.py makemigrations
python manage.py migrate
```

6. **Crear roles y permisos por defecto**:
```bash
python manage.py crear_permisos_default
python manage.py crear_roles_default
```

7. **Crear superusuario**:
```bash
python manage.py crear_superuser
# O usar el comando interactivo:
python manage.py createsuperuser
```

8. **Iniciar el servidor**:
```bash
python manage.py runserver 0.0.0.0:8000
```

✅ **La API estará disponible en**: http://localhost:8000/api/

---

## 🔧 Configuración de Variables de Entorno

Archivo `.env` - Variables principales:

```env
# Django
DEBUG=True
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_NAME=iot_sensor_db
DB_USER=iot_user
DB_PASSWORD=iot_password_123
DB_HOST=postgres  # 'localhost' sin Docker
DB_PORT=5432

# JWT
JWT_ACCESS_TOKEN_LIFETIME=60        # minutos
JWT_REFRESH_TOKEN_LIFETIME=1440     # minutos (24 horas)

# CORS
CORS_ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173

# EMQX (Para Fase 3)
EMQX_BROKER_HOST=localhost
EMQX_BROKER_PORT=1883
EMQX_USERNAME=admin
EMQX_PASSWORD=public
```

---

## 📚 Endpoints de la API

### 🔐 Autenticación

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/auth/register/` | Registrar nuevo usuario |
| POST | `/api/auth/login/` | Iniciar sesión (obtener JWT) |
| POST | `/api/auth/refresh/` | Renovar token de acceso |
| GET | `/api/users/me/` | Obtener perfil del usuario actual |

### 👥 Usuarios

| Método | Endpoint | Descripción | Permisos |
|--------|----------|-------------|----------|
| GET | `/api/users/` | Listar usuarios | Superusuario |
| POST | `/api/users/` | Crear usuario | Superusuario |
| GET | `/api/users/{id}/` | Ver detalle de usuario | Superusuario |
| PUT/PATCH | `/api/users/{id}/` | Actualizar usuario | Superusuario |
| DELETE | `/api/users/{id}/` | Eliminar usuario | Superusuario |
| POST | `/api/users/{id}/activate/` | Activar usuario | Superusuario |
| POST | `/api/users/{id}/deactivate/` | Desactivar usuario | Superusuario |

### 🎭 Roles y Permisos

| Método | Endpoint | Descripción | Permisos |
|--------|----------|-------------|----------|
| GET | `/api/roles/` | Listar roles | Superusuario |
| POST | `/api/roles/` | Crear rol | Superusuario |
| GET | `/api/permisos/` | Listar permisos | Superusuario |
| POST | `/api/permisos/` | Crear permiso | Superusuario |

### 📡 Sensores

| Método | Endpoint | Descripción | Permisos |
|--------|----------|-------------|----------|
| GET | `/api/sensors/` | Listar sensores | Autenticado |
| POST | `/api/sensors/` | Crear sensor | Superusuario/Operador |
| GET | `/api/sensors/{id}/` | Ver detalle de sensor | Autenticado |
| PUT/PATCH | `/api/sensors/{id}/` | Actualizar sensor | Superusuario/Propietario |
| DELETE | `/api/sensors/{id}/` | Eliminar sensor | Superusuario/Propietario |
| GET | `/api/sensors/available/` | Sensores disponibles | Autenticado |
| GET | `/api/sensors/tipos/` | Tipos de sensores | Autenticado |

### 🖥️ Dispositivos

| Método | Endpoint | Descripción | Permisos |
|--------|----------|-------------|----------|
| GET | `/api/devices/` | Listar dispositivos | Autenticado |
| POST | `/api/devices/` | Crear dispositivo | Superusuario/Operador |
| GET | `/api/devices/{id}/` | Ver detalle de dispositivo | Autenticado |
| PUT/PATCH | `/api/devices/{id}/` | Actualizar dispositivo | Superusuario/Operador asignado |
| DELETE | `/api/devices/{id}/` | Eliminar dispositivo | Superusuario |
| POST | `/api/devices/{id}/assign-sensor/` | Asignar sensor | Superusuario/Operador |
| POST | `/api/devices/{id}/assign-operator/` | Asignar operador | Superusuario |
| DELETE | `/api/devices/{id}/remove-sensor/` | Remover sensor | Superusuario/Operador |
| GET | `/api/devices/tipos/` | Tipos de dispositivos | Autenticado |

### 📊 Lecturas

| Método | Endpoint | Descripción | Permisos |
|--------|----------|-------------|----------|
| GET | `/api/readings/` | Listar lecturas | Autenticado |
| POST | `/api/readings/` | Crear lectura | Superusuario/Operador |
| GET | `/api/readings/{id}/` | Ver detalle de lectura | Autenticado |
| POST | `/api/readings/bulk/` | Crear múltiples lecturas | Superusuario/Operador |
| GET | `/api/readings/estadisticas/` | Estadísticas de lecturas | Autenticado |

### 📈 Dashboard

| Método | Endpoint | Descripción | Permisos |
|--------|----------|-------------|----------|
| GET | `/api/dashboard/stats/` | Estadísticas del sistema | Autenticado |

---

## 🔑 Ejemplos de Uso con cURL

### Registro de usuario
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "nuevo_usuario",
    "email": "usuario@example.com",
    "password": "password123",
    "password_confirm": "password123",
    "first_name": "Nombre",
    "last_name": "Apellido",
    "tipo_usuario": "externo"
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "admin123"
  }'
```

### Crear sensor (con token)
```bash
curl -X POST http://localhost:8000/api/sensors/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "nombre": "Sensor DHT22",
    "tipo": "temperatura",
    "unidad_medida": "°C",
    "rango_min": -40,
    "rango_max": 80,
    "estado": "activo"
  }'
```

### Asignar sensor a dispositivo
```bash
curl -X POST http://localhost:8000/api/devices/1/assign-sensor/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "sensor_id": 1,
    "configuracion_json": {"intervalo": 60}
  }'
```

### Crear lectura
```bash
curl -X POST http://localhost:8000/api/readings/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "dispositivo": 1,
    "sensor": 1,
    "valor": 25.5,
    "metadata_json": {"ubicacion": "sala"}
  }'
```

---

## 📖 Documentación de la API

Una vez que el servidor esté corriendo, puedes acceder a la documentación interactiva en:

- **Swagger UI**: http://localhost:8000/api/docs/
- **ReDoc**: http://localhost:8000/api/redoc/
- **Schema JSON**: http://localhost:8000/api/schema/

También puedes acceder al panel de administración de Django:
- **Admin**: http://localhost:8000/admin/

---

## 👥 Usuarios y Roles por Defecto

### Superusuario (creado con comando)
- **Username**: admin
- **Password**: admin123
- **Permisos**: Acceso completo

### Roles del Sistema
1. **Superusuario**: Acceso completo al sistema
2. **Operador**: Puede gestionar dispositivos asignados, sensores y lecturas
3. **Solo Lectura**: Solo puede visualizar información

Para crear usuarios adicionales, utiliza el endpoint `/api/auth/register/` o el panel de administración.

---

## 📁 Estructura del Proyecto

```
iot_sensor_platform/
├── apps/                         # Apps modulares
│   ├── accounts/                 # Gestión de usuarios y autenticación
│   │   ├── management/
│   │   │   └── commands/
│   │   │       ├── crear_permisos_default.py
│   │   │       ├── crear_roles_default.py
│   │   │       └── crear_superuser.py
│   │   ├── migrations/
│   │   ├── admin.py
│   │   ├── models.py             # CustomUser, Rol, Permiso
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   └── permissions.py
│   ├── sensors/                  # Gestión de sensores
│   │   ├── migrations/
│   │   ├── admin.py
│   │   ├── models.py             # Sensor, TipoSensor
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── urls.py
│   ├── devices/                  # Gestión de dispositivos IoT
│   │   ├── migrations/
│   │   ├── admin.py
│   │   ├── models.py             # Dispositivo, DispositivoSensor
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── urls.py
│   ├── readings/                 # Gestión de lecturas
│   │   ├── migrations/
│   │   ├── admin.py
│   │   ├── models.py             # Lectura
│   │   ├── serializers.py
│   │   ├── views.py
│   │   └── urls.py
│   └── mqtt/                     # Integración MQTT/EMQX
│       ├── management/
│       │   └── commands/
│       │       └── configurar_mqtt_default.py
│       ├── migrations/
│       ├── admin.py
│       ├── models.py             # MQTTBroker, MQTTCredential, etc.
│       ├── serializers.py
│       ├── views.py
│       └── urls.py
├── config/                       # Configuración del proyecto
│   ├── settings.py               # Settings de Django
│   ├── urls.py                   # URLs principales
│   ├── asgi.py
│   └── wsgi.py
├── logs/                         # Logs de la aplicación
├── Dockerfile                    # Dockerfile para Django
├── docker-compose.yml            # Configuración Docker Compose
├── docker-entrypoint.sh          # Script de entrada Docker
├── requirements.txt              # Dependencias Python
├── .env.example                  # Ejemplo de variables de entorno
├── .gitignore                    # Archivos ignorados por Git
├── manage.py                     # Script de gestión Django
├── README.md                     # Este archivo
├── API_DOCUMENTATION.md          # Documentación detallada de API
└── MODELO_ER.md                  # Diagrama Entidad-Relación
```

---

## 🧪 Comandos Útiles

### Comandos Django

```bash
# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Crear superusuario personalizado
python manage.py crear_superuser

# Crear roles por defecto
python manage.py crear_roles_default

# Crear permisos por defecto
python manage.py crear_permisos_default

# Ejecutar tests
python manage.py test

# Shell de Django
python manage.py shell

# Recolectar archivos estáticos
python manage.py collectstatic
```

### Comandos Docker

```bash
# Construir y levantar servicios
docker-compose up --build

# Levantar en segundo plano
docker-compose up -d

# Ver logs
docker-compose logs -f django

# Ejecutar comando en contenedor
docker-compose exec django python manage.py <comando>

# Detener servicios
docker-compose down

# Eliminar volúmenes (⚠️ CUIDADO: elimina la BD)
docker-compose down -v
```

---

## 🔒 Seguridad

- ✅ Tokens JWT para autenticación
- ✅ Contraseñas hasheadas con PBKDF2
- ✅ Validación de permisos por rol
- ✅ CORS configurado
- ✅ Variables de entorno para credenciales
- ✅ Validación de datos en serializers
- ⚠️ **IMPORTANTE**: Cambiar SECRET_KEY en producción
- ⚠️ Establecer DEBUG=False en producción
- ⚠️ Configurar ALLOWED_HOSTS apropiadamente

---

## 🐛 Troubleshooting

### Error de conexión a PostgreSQL
```bash
# Verificar que PostgreSQL esté corriendo
docker-compose ps
# O sin Docker:
sudo systemctl status postgresql
```

### Permisos negados en endpoints
- Verificar que el token JWT sea válido
- Verificar que el usuario tenga el rol apropiado

### Lecturas fuera de rango
- Verificar que el valor esté dentro del rango_min y rango_max del sensor

---

## 📋 TODO - Próximas Fases

- [ ] **Fase 2**: Frontend React con dashboard y visualizaciones
- [ ] **Fase 3**: Integración con EMQX para MQTT en tiempo real
- [ ] **Fase 4**: Sistema de alertas y notificaciones
- [ ] **Fase 5**: Análisis de datos y predicciones con ML

---

## 📄 Licencia

Este proyecto es de uso privado/educativo.

---

## 👨‍💻 Autor

Desarrollado con Django REST Framework y PostgreSQL para gestión de plataforma IoT.

---

## 📞 Soporte

Para soporte adicional, consulta:
- [API_DOCUMENTATION.md](./API_DOCUMENTATION.md) - Documentación detallada de endpoints
- [MODELO_ER.md](./MODELO_ER.md) - Modelo de datos y relaciones
- Documentación interactiva: http://localhost:8000/api/docs/

---

**⚠️ NOTA IMPORTANTE**: Este localhost (127.0.0.1) se refiere al localhost de la computadora que está ejecutando el servidor Django, no a tu máquina local. Para acceder de forma local o remota, necesitarás desplegar la aplicación en tu propio sistema o servidor.
