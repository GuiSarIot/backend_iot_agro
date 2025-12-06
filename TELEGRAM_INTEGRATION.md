# Ejemplo de Bot de Telegram para IoT Sensor Platform

Este documento muestra cómo crear un bot de Telegram básico para integrarse con la plataforma.

## 1. Crear el Bot en Telegram

1. Habla con [@BotFather](https://t.me/BotFather) en Telegram
2. Envía `/newbot`
3. Elige un nombre: `IoT Sensor Platform Bot`
4. Elige un username: `tu_bot_iot_bot`
5. Recibirás el **token del bot** (guárdalo en .env)

## 2. Configuración en .env

```bash
# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN=123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11
TELEGRAM_BOT_USERNAME=tu_bot_iot_bot
```

## 3. Ejemplo de Bot Básico (Python)

Crear archivo: `telegram_bot.py`

```python
"""
Bot de Telegram para IoT Sensor Platform
Ejecutar: python telegram_bot.py
"""

import os
import requests
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from decouple import config

# Configuración
TELEGRAM_BOT_TOKEN = config('TELEGRAM_BOT_TOKEN')
API_BASE_URL = config('API_BASE_URL', default='http://localhost:8000/api')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /start - Bienvenida"""
    chat_id = update.effective_chat.id
    user = update.effective_user
    
    welcome_message = f"""
🤖 ¡Bienvenido al Bot IoT Sensor Platform!

📱 Tu Chat ID: `{chat_id}`
👤 Usuario: @{user.username if user.username else 'Sin username'}

📋 Comandos disponibles:
/start - Este mensaje
/link - Vincular tu cuenta
/status - Ver estado de dispositivos
/help - Ayuda

Para vincular tu cuenta:
1. Genera un código en la web
2. Usa /link CODIGO
"""
    
    await update.message.reply_text(welcome_message, parse_mode='Markdown')


async def link_account(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /link CODIGO - Vincular cuenta"""
    chat_id = update.effective_chat.id
    username = update.effective_user.username or ''
    
    # Verificar que se proporcionó el código
    if not context.args:
        await update.message.reply_text(
            "❌ Uso: /link CODIGO\n\n"
            "Genera un código en la plataforma web y úsalo aquí."
        )
        return
    
    verification_code = context.args[0].upper()
    
    # Buscar usuario por código en la API
    try:
        # Llamar al endpoint de vinculación
        response = requests.post(
            f"{API_BASE_URL}/telegram/link-account/",
            json={
                "chat_id": str(chat_id),
                "username": f"@{username}" if username else "",
                "verification_code": verification_code,
                # El user_id se busca automáticamente por el código
            },
            headers={
                "X-Telegram-Bot-Token": TELEGRAM_BOT_TOKEN
            },
            timeout=10
        )
        
        data = response.json()
        
        if response.status_code == 200 and data.get('success'):
            await update.message.reply_text(
                f"✅ ¡Cuenta vinculada exitosamente!\n\n"
                f"Usuario: {data['username']}\n"
                f"Ahora recibirás notificaciones de la plataforma."
            )
        else:
            error_msg = data.get('message', 'Error desconocido')
            await update.message.reply_text(f"❌ Error: {error_msg}")
    
    except requests.RequestException as e:
        await update.message.reply_text(
            f"❌ Error de conexión: {str(e)}\n\n"
            f"Verifica que la API esté funcionando."
        )


async def check_status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /status - Ver estado de dispositivos"""
    chat_id = update.effective_chat.id
    
    await update.message.reply_text(
        "📊 Consultando estado de tus dispositivos...\n\n"
        "⚙️ En desarrollo: Esta funcionalidad mostrará el estado "
        "de tus dispositivos IoT en tiempo real."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Comando /help - Ayuda"""
    help_text = """
📖 **Ayuda - Bot IoT Sensor Platform**

**Vinculación de cuenta:**
1. Inicia sesión en la plataforma web
2. Ve a tu perfil → Telegram
3. Genera un código de verificación
4. Envía `/link CODIGO` aquí

**Notificaciones:**
Recibirás alertas sobre:
• 🔌 Dispositivos desconectados
• ⚠️ Lecturas fuera de rango
• 🔧 Cambios en configuración
• 📊 Reportes programados

**Comandos:**
/start - Mensaje de bienvenida
/link CODIGO - Vincular cuenta
/status - Estado de dispositivos
/help - Esta ayuda

**Soporte:**
Si tienes problemas, contacta al administrador del sistema.
"""
    
    await update.message.reply_text(help_text, parse_mode='Markdown')


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Maneja mensajes de texto generales"""
    text = update.message.text.strip().upper()
    
    # Si el mensaje parece un código de verificación (8 caracteres hexadecimales)
    if len(text) == 8 and all(c in '0123456789ABCDEF' for c in text):
        # Intentar vincular con este código
        context.args = [text]
        await link_account(update, context)
    else:
        await update.message.reply_text(
            "👋 ¡Hola! Usa /help para ver los comandos disponibles.\n\n"
            "Si intentas vincular tu cuenta, usa: /link CODIGO"
        )


def main():
    """Función principal del bot"""
    print(f"🤖 Iniciando Bot IoT Sensor Platform...")
    print(f"📡 API Base URL: {API_BASE_URL}")
    
    # Crear aplicación
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    
    # Registrar handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("link", link_account))
    application.add_handler(CommandHandler("status", check_status))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Iniciar bot
    print("✅ Bot iniciado y esperando mensajes...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
```

## 4. Instalar dependencias del bot

```bash
pip install python-telegram-bot==20.7
```

## 5. Ejecutar el bot

```bash
python telegram_bot.py
```

## 6. Flujo de Vinculación

### Desde la Web (usuario):
```bash
# 1. Usuario genera código
POST /api/telegram/generate-verification/
Response: {"verification_code": "A1B2C3D4", "expires_in_minutes": 15}

# 2. Usuario verifica su ID de Telegram (opcional)
GET /api/telegram/status/
Response: {"is_linked": false, "telegram_username": null}
```

### Desde Telegram (usuario):
```
Usuario: /link A1B2C3D4
Bot: ✅ ¡Cuenta vinculada exitosamente!
```

### Desde el Backend (bot):
```bash
# El bot llama automáticamente
POST /api/telegram/link-account/
Headers: {"X-Telegram-Bot-Token": "tu_token"}
Body: {
    "user_id": 1,
    "chat_id": "1393684739",
    "username": "@tu_username",
    "verification_code": "A1B2C3D4"
}
```

## 7. Enviar Notificaciones desde Django

### En views.py o signals.py:

```python
from apps.accounts.telegram_helper import telegram_notifier

# Notificar a un usuario específico
user = CustomUser.objects.get(id=1)
if user.can_receive_telegram_notifications:
    telegram_notifier.send_notification_to_user(
        user,
        "Tu dispositivo 'Sensor-01' se ha desconectado",
        notification_type='warning'
    )

# Notificar sobre dispositivo
from apps.devices.models import Dispositivo
device = Dispositivo.objects.get(id=1)
telegram_notifier.send_device_alert(
    device,
    alert_type='offline',
    message='El dispositivo no responde desde hace 5 minutos'
)

# Notificar sobre lectura fuera de rango
from apps.readings.models import Lectura
lectura = Lectura.objects.latest('timestamp')
telegram_notifier.send_reading_alert(
    lectura,
    lectura.sensor,
    threshold_type='max'
)

# Enviar a todos los superusuarios
from apps.accounts.models import CustomUser
superusers = CustomUser.objects.filter(
    is_superuser=True,
    telegram_verified=True,
    telegram_notifications_enabled=True
)
telegram_notifier.send_notification_to_users(
    superusers,
    "Sistema actualizado exitosamente a v2.0",
    notification_type='success'
)
```

## 8. Tu Información de Telegram

**Tu Chat ID:** `1393684739`

Para vincular tu cuenta manualmente (desarrollo):

```python
# En Django shell
python manage.py shell

from apps.accounts.models import CustomUser
user = CustomUser.objects.get(username='tu_usuario')
user.telegram_chat_id = '1393684739'
user.telegram_username = '@tu_username'
user.telegram_verified = True
user.telegram_notifications_enabled = True
user.save()
```

## 9. Probar Notificaciones

Una vez vinculada tu cuenta:

```bash
# Desde API (como superusuario)
POST /api/telegram/send-notification/
Body: {
    "message": "Mensaje de prueba desde la plataforma IoT",
    "user_ids": [1],
    "notification_type": "info"
}
```

## 10. Seguridad

- ✅ El bot requiere token en header `X-Telegram-Bot-Token`
- ✅ Códigos de verificación expiran en 15 minutos
- ✅ Solo usuarios verificados reciben notificaciones
- ✅ Los usuarios pueden desactivar notificaciones
- ⚠️ **NUNCA** commits el `TELEGRAM_BOT_TOKEN` en Git

## Referencias

- Bot API: https://core.telegram.org/bots/api
- python-telegram-bot: https://python-telegram-bot.org/
- Documentación interna: `.github/copilot-instructions.md`
