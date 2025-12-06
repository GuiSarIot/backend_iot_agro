"""
Script simple para probar el bot de Telegram
Ejecutar: python test_telegram.py
"""

import requests
from decouple import config

TELEGRAM_BOT_TOKEN = config('TELEGRAM_BOT_TOKEN')
CHAT_ID = '1393684739'  # Tu chat ID

def send_test_message():
    """Envía un mensaje de prueba"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    payload = {
        'chat_id': CHAT_ID,
        'text': '🤖 <b>Prueba de Bot IoT Platform</b>\n\n✅ El bot está funcionando correctamente!\n\n📱 Este mensaje fue enviado desde el script de prueba.',
        'parse_mode': 'HTML'
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        data = response.json()
        
        if data.get('ok'):
            print("✅ Mensaje enviado exitosamente!")
            print(f"📨 Message ID: {data['result']['message_id']}")
            return True
        else:
            print(f"❌ Error: {data.get('description')}")
            print(f"💡 Asegúrate de haber iniciado el bot con /start en Telegram")
            return False
    
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

def get_bot_info():
    """Obtiene información del bot"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/getMe"
    
    try:
        response = requests.get(url, timeout=10)
        data = response.json()
        
        if data.get('ok'):
            bot = data['result']
            print("\n🤖 Información del Bot:")
            print(f"   Nombre: {bot['first_name']}")
            print(f"   Username: @{bot['username']}")
            print(f"   ID: {bot['id']}")
            print(f"   Puede unirse a grupos: {bot.get('can_join_groups', False)}")
            return True
        else:
            print(f"❌ Error obteniendo info del bot: {data.get('description')}")
            return False
    
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return False

if __name__ == '__main__':
    print("="*60)
    print("🧪 TEST DE BOT DE TELEGRAM - IoT Sensor Platform")
    print("="*60)
    
    # Verificar token
    if not TELEGRAM_BOT_TOKEN or TELEGRAM_BOT_TOKEN == '':
        print("❌ TELEGRAM_BOT_TOKEN no configurado en .env")
        exit(1)
    
    print(f"\n📋 Configuración:")
    print(f"   Chat ID: {CHAT_ID}")
    print(f"   Token configurado: {'✅' if TELEGRAM_BOT_TOKEN else '❌'}")
    
    # Obtener info del bot
    print("\n" + "-"*60)
    if not get_bot_info():
        print("\n⚠️  Verifica que el TELEGRAM_BOT_TOKEN sea correcto")
        exit(1)
    
    # Enviar mensaje de prueba
    print("\n" + "-"*60)
    print("\n📤 Enviando mensaje de prueba...")
    
    if send_test_message():
        print("\n✅ ¡Todo funciona correctamente!")
        print("\n📱 Próximos pasos:")
        print("   1. Verifica que recibiste el mensaje en Telegram")
        print("   2. Si no lo recibiste, inicia el bot con /start")
        print("   3. Ejecuta este script de nuevo")
    else:
        print("\n⚠️  Si ves 'chat not found', haz esto:")
        print("   1. Abre Telegram")
        print("   2. Busca tu bot por username")
        print("   3. Envía /start al bot")
        print("   4. Ejecuta este script nuevamente")
    
    print("\n" + "="*60)
