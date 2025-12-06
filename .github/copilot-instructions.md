# Copilot Instructions - IoT Sensor Platform

## Project Overview
Django REST Framework backend for IoT sensor and device management with MQTT integration. **Key characteristic**: Highly modular app-based architecture with role-based permissions and MQTT-ready infrastructure.

## Architecture

### Modular App Structure
```
apps/
├── accounts/    # Authentication, roles, permissions, AuditLog, AccessLog
├── sensors/     # Sensor management (temperature, humidity, pressure, etc.)
├── devices/     # IoT devices (Raspberry Pi, ESP32, Arduino)
├── readings/    # Sensor readings with MQTT metadata
└── mqtt/        # MQTT broker config, credentials (encrypted), topics, EMQX
```

**Critical**: Each app is self-contained with its own models, views, serializers, permissions, urls, admin, and migrations. Never mix concerns across apps.

### Custom Database Tables
Models use Spanish table names via `Meta.db_table`:
- `CustomUser` → `users`
- `Dispositivo` → `dispositivos`
- `Lectura` → `lecturas`
- `BrokerConfig` → `mqtt_broker_config`

Always check `models.py` for the actual table name before writing raw SQL or debugging DB issues.

### Permission System
Three-tier role system (`Rol` model):
- **superusuario**: Full access
- **operador**: Manages assigned devices only
- **solo_lectura**: Read-only

Custom permission classes in `apps/accounts/permissions.py`:
- `IsSuperuser`, `CanManageDevices`, `CanManageSensors`, `CanCreateReadings`, `CanManageMQTT`
- Always use these classes in ViewSet `permission_classes`, never check `is_superuser` manually in views

**Operator filtering pattern** (see `apps/devices/views.py:38-41`):
```python
if not self.request.user.is_superuser:
    if self.request.user.rol and self.request.user.rol.nombre == 'operador':
        queryset = queryset.filter(operador_asignado=self.request.user)
```

## Key Patterns

### ViewSets Structure
All CRUD endpoints use `ModelViewSet` with:
- `select_related()` / `prefetch_related()` for performance (see `DispositivoViewSet`)
- Custom `@action` methods for business logic (assign sensors, bulk operations)
- Filtered querysets respecting user roles
- Search and ordering filters enabled

### MQTT Integration Points
Models have MQTT-specific fields:
- `Dispositivo`: `mqtt_client_id`, `mqtt_enabled`, `connection_status`, `last_seen`
- `Lectura`: `mqtt_message_id`, `mqtt_qos`, `mqtt_retained`
- `Sensor`: `mqtt_topic_suffix`, `publish_interval`

**EMQX Authentication & Authorization** (PostgreSQL-based):
- `EMQXUser`: MQTT user authentication (table: `mqtt_user`)
  - Password hashing: `SHA256(password + salt)` - use `set_password()` method
  - Supports superuser flag for unrestricted access
  - **Auto-created** via Django signals when `Dispositivo` is created
- `EMQXACL`: Access Control Lists (table: `mqtt_acl`)
  - Defines publish/subscribe permissions per user
  - Supports topic wildcards: `+` (single level), `#` (multi-level)
  - **Auto-generated** default rules for each device (5 rules: publish sensors/status, subscribe commands/config, deny all else)

**Automatic Sync** (`apps/mqtt/signals.py`):
- Creating `Dispositivo` → Auto-creates `EMQXUser` + default ACL rules
- Deleting `Dispositivo` → Auto-deletes `EMQXUser` (CASCADE removes ACL rules)
- Username pattern: `device_{identificador_unico}`
- Password: 24-char random token (logged once on creation)

Topic pattern: `iot/sensors/{device_id}/data` (see `MQTT_INTEGRATION.md`)

### Management Commands
Located in `apps/*/management/commands/`:
- `crear_superuser.py`: Creates admin (username: admin, password: admin123)
- `crear_roles_default.py`: Seeds 3 roles
- `crear_permisos_default.py`: Seeds 13 system permissions
- `configurar_mqtt_default.py`: MQTT broker defaults
- `crear_usuarios_emqx_default.py`: Creates EMQX users and ACL rules

**Initialization sequence** (see `docker-entrypoint.sh`):
1. Migrations → 2. Permissions → 3. Roles → 4. MQTT config → 5. Superuser → 6. EMQX users (optional)

## Development Workflows

### Local Setup
```bash
# With Docker (recommended)
docker-compose up --build
docker-compose exec django python manage.py crear_superuser

# Without Docker
python -m venv venv
pip install -r requirements.txt
python manage.py migrate
python manage.py crear_permisos_default
python manage.py crear_roles_default
python manage.py crear_superuser
```

### Adding New Features
1. **New model**: Add to appropriate app, set `db_table` in Meta, add indexes for FK/status fields
2. **New permission**: Add to `crear_permisos_default.py` command, create permission class in `permissions.py`
3. **New endpoint**: Create ViewSet with permission classes, register in app's `urls.py` router
4. **New app**: Add to `INSTALLED_APPS` as `apps.<app_name>`, create URL include in `config/urls.py`

### Testing Changes
```bash
# Run migrations
python manage.py makemigrations
python manage.py migrate

# Access API
# Docs: http://localhost:8000/api/docs/
# Admin: http://localhost:8000/admin/
```

## Configuration

### Environment Variables
Uses `python-decouple` for config (`.env` file):
- `DB_*`: PostgreSQL connection
- `JWT_*_LIFETIME`: Token durations (default 60min access, 1440min refresh)
- `DEBUG`, `SECRET_KEY`, `ALLOWED_HOSTS`
- `EMQX_*`: MQTT broker settings (Phase 3)

### JWT Authentication
SimpleJWT with token rotation enabled. All endpoints require `Authorization: Bearer <token>` except:
- `/api/auth/register/`
- `/api/auth/login/`
- `/api/auth/token/refresh/`

### API Documentation
Auto-generated via `drf-spectacular`:
- Swagger UI: `/api/docs/`
- ReDoc: `/api/redoc/`
- OpenAPI schema: `/api/schema/`

## Security Features

### Password Encryption (MQTT)
All MQTT passwords (BrokerConfig, MQTTCredential) are encrypted using Fernet (AES):
- Use `set_password(raw_password)` to encrypt
- Use `get_password()` to decrypt
- Key stored in `settings.MQTT_ENCRYPTION_KEY`
- Generate new key: `python manage.py generar_clave_encriptacion`
- Migrate existing: `python manage.py migrar_passwords_mqtt`

### Telegram Integration
Users can link Telegram accounts for notifications:
- Fields: `telegram_chat_id`, `telegram_username`, `telegram_verified`, `telegram_notifications_enabled`
- Verification flow: Generate code → User sends to bot → Bot calls link endpoint
- Helper: `telegram_helper.TelegramNotifier` for sending notifications
- Endpoints: `/api/telegram/generate-verification/`, `/api/telegram/link-account/`, `/api/telegram/send-notification/`
- Property: `user.can_receive_telegram_notifications` checks if user can receive alerts

### Email Integration
Users can receive notifications via email with HTML templates:
- Fields: `email_notifications_enabled`, `email_verified`, `email_verification_token`, `email_verification_sent_at`
- Verification flow: Send verification email → User clicks link (24h expiry) → Email verified
- Helper: `email_helper.EmailNotifier` for sending emails (simple, HTML, alerts)
- Endpoints: `/api/email/send-verification/`, `/api/email/verify/`, `/api/email/preferences/`, `/api/email/send-notification/`, `/api/email/status/`
- Property: `user.can_receive_email_notifications` checks if user can receive emails
- Templates: Professional HTML emails with responsive design, colored by notification type
- SMTP Config: Supports Gmail (app passwords), Outlook, SendGrid, Amazon SES
- Documentation: `EMAIL_INTEGRATION.md`

### Audit Logging
`AuditLog` model tracks CREATE/UPDATE/DELETE on critical models:
- Auto-captured via middleware: user, IP, user_agent, changes
- Endpoints: `/api/audit-logs/` (superuser only)
- Stats: `/api/audit-logs/stats/`

### Access Logging
`AccessLog` model tracks ALL API requests:
- Auto-captured via `AccessLogMiddleware`: module, endpoint, method, status, response_time
- Endpoints: `/api/access-logs/` (users see own, superusers see all)
- Stats: `/api/access-logs/stats/`
- Manual creation: `POST /api/access-logs/create-log/`

**Important**: Both middleware are in `apps/accounts/middleware.py` and enabled in `MIDDLEWARE` setting.

## Common Pitfalls

1. **ForeignKey references**: Use string references for cross-app models: `'devices.Dispositivo'` not direct import
2. **Migrations**: Always run `crear_permisos_default` after adding permission-related models
3. **Operator permissions**: Remember `get_queryset()` filtering – operators see only assigned devices
4. **MQTT fields**: Nullable/blank by default, don't assume presence in queries
5. **Spanish naming**: Models use Spanish (`Dispositivo`, `Lectura`) but code/comments mix Spanish/English
6. **Password encryption**: Never access `.password` directly on MQTT models, use `get_password()`
7. **Audit logs**: Read-only via API, only superusers can delete in admin

## References
- Architecture details: `PROJECT_SUMMARY.md`
- MQTT setup: `MQTT_INTEGRATION.md`
- Telegram setup: `TELEGRAM_INTEGRATION.md`
- Email setup: `EMAIL_INTEGRATION.md`
- Refactoring history: `REFACTORIZATION_SUMMARY.md`
- Test users: `USUARIOS_PRUEBA.md`
