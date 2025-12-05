# Guía de Integración MQTT/EMQX

## Descripción General

Esta plataforma IoT incluye soporte completo para MQTT (Message Queuing Telemetry Transport) mediante EMQX, un broker MQTT de alto rendimiento. Los dispositivos IoT pueden publicar lecturas de sensores y recibir comandos a través de MQTT.

## Arquitectura MQTT

```
┌─────────────────┐         ┌──────────────┐         ┌─────────────────┐
│  Dispositivos   │◄───────►│  EMQX Broker │◄───────►│   Backend API   │
│  IoT (ESP32,    │  MQTT   │  (Port 1883) │  HTTP   │   (Django REST) │
│  Raspberry Pi)  │         │              │         │                 │
└─────────────────┘         └──────────────┘         └─────────────────┘
                                   ▲
                                   │
                                   ▼
                            ┌──────────────┐
                            │   Dashboard  │
                            │  WebSocket   │
                            └──────────────┘
```

## Componentes MQTT

### 1. BrokerConfig
Configuración del broker MQTT (EMQX).

**Campos:**
- `nombre`: Nombre identificador
- `host`: Dirección del broker (ej: localhost, emqx.io)
- `port`: Puerto (1883 para MQTT, 8883 para MQTTS)
- `protocol`: mqtt | mqtts | ws | wss
- `username/password`: Credenciales de autenticación
- `keepalive`: Intervalo de keep-alive
- `use_tls`: Conexión segura con TLS

### 2. MQTTCredential
Credenciales MQTT únicas por dispositivo.

**Campos:**
- `dispositivo`: Dispositivo asociado (OneToOne)
- `client_id`: ID único del cliente MQTT
- `username/password`: Credenciales del dispositivo
- `use_device_cert`: Usar certificados X.509
- `client_cert/client_key`: Certificados del dispositivo

### 3. MQTTTopic
Topics MQTT para publicación/suscripción.

**Campos:**
- `nombre`: Nombre descriptivo
- `topic_pattern`: Patrón del topic (ej: `sensors/{device_id}/data`)
- `tipo`: publish | subscribe | both
- `qos`: Quality of Service (0, 1, 2)
- `retain`: Retener último mensaje

### 4. DeviceMQTTConfig
Configuración MQTT específica por dispositivo.

**Campos:**
- `dispositivo`: Dispositivo asociado
- `broker`: Broker MQTT a usar
- `publish_topic`: Topic principal de publicación
- `subscribe_topics`: Topics de suscripción
- `publish_interval`: Intervalo de publicación (segundos)
- `connection_status`: Estado actual (connected/disconnected/error)

## Patrones de Topics

### Nomenclatura Estándar

```
iot/sensors/{device_id}/data          # Datos de sensores
iot/devices/{device_id}/status        # Estado del dispositivo
iot/devices/{device_id}/commands      # Comandos al dispositivo
iot/alerts/{device_id}                # Alertas críticas
```

### Variables en Topics

- `{device_id}`: ID único del dispositivo
- `{sensor_type}`: Tipo de sensor (temperature, humidity, etc.)
- `{timestamp}`: Timestamp Unix

## Quality of Service (QoS)

| QoS | Descripción | Uso Recomendado |
|-----|-------------|-----------------|
| 0 | At most once | Datos no críticos, alta frecuencia |
| 1 | At least once | Datos importantes (Default) |
| 2 | Exactly once | Comandos críticos, alertas |

## Configuración Inicial

### 1. Configurar Broker EMQX

```bash
# Usando Docker Compose (recomendado)
docker-compose up -d emqx

# Acceder al dashboard EMQX
# URL: http://localhost:18083
# User: admin
# Pass: public
```

### 2. Crear Configuración desde API

```bash
# Crear broker
curl -X POST http://localhost:8000/api/mqtt/brokers/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "EMQX Production",
    "host": "emqx",
    "port": 1883,
    "protocol": "mqtt",
    "username": "admin",
    "password": "public",
    "keepalive": 60,
    "is_active": true
  }'

# Crear topics
curl -X POST http://localhost:8000/api/mqtt/topics/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Datos de Sensores",
    "topic_pattern": "iot/sensors/{device_id}/data",
    "tipo": "publish",
    "qos": 1,
    "retain": false
  }'
```

### 3. Configurar Dispositivo

```bash
# Crear credenciales MQTT
curl -X POST http://localhost:8000/api/mqtt/credentials/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "dispositivo": 1,
    "client_id": "ESP32_001",
    "username": "device_001",
    "password": "secure_password",
    "is_active": true
  }'

# Configurar MQTT del dispositivo
curl -X POST http://localhost:8000/api/mqtt/device-config/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "dispositivo": 1,
    "broker": 1,
    "publish_topic": 1,
    "subscribe_topics": [2],
    "publish_interval": 60,
    "qos": 1,
    "auto_reconnect": true
  }'
```

## Código de Ejemplo - Dispositivo IoT

### ESP32 (Arduino)

```cpp
#include <WiFi.h>
#include <PubSubClient.h>

// WiFi
const char* ssid = "YOUR_SSID";
const char* password = "YOUR_PASSWORD";

// MQTT
const char* mqtt_server = "192.168.1.100";
const int mqtt_port = 1883;
const char* mqtt_user = "device_001";
const char* mqtt_password = "secure_password";
const char* mqtt_client_id = "ESP32_001";

// Topics
const char* topic_data = "iot/sensors/ESP32_001/data";
const char* topic_commands = "iot/devices/ESP32_001/commands";

WiFiClient espClient;
PubSubClient client(espClient);

void setup() {
  Serial.begin(115200);
  setup_wifi();
  client.setServer(mqtt_server, mqtt_port);
  client.setCallback(callback);
}

void setup_wifi() {
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi conectado");
}

void callback(char* topic, byte* payload, unsigned int length) {
  String message = "";
  for (int i = 0; i < length; i++) {
    message += (char)payload[i];
  }
  Serial.println("Comando recibido: " + message);
  // Procesar comando
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Conectando a MQTT...");
    if (client.connect(mqtt_client_id, mqtt_user, mqtt_password)) {
      Serial.println("conectado");
      client.subscribe(topic_commands);
    } else {
      Serial.print("falló, rc=");
      Serial.print(client.state());
      delay(5000);
    }
  }
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();
  
  // Publicar datos cada 60 segundos
  static unsigned long lastMsg = 0;
  unsigned long now = millis();
  if (now - lastMsg > 60000) {
    lastMsg = now;
    
    // Leer sensores
    float temperature = readTemperature();
    float humidity = readHumidity();
    
    // Crear JSON
    String payload = "{";
    payload += "\"device_id\":\"ESP32_001\",";
    payload += "\"temperature\":" + String(temperature) + ",";
    payload += "\"humidity\":" + String(humidity) + ",";
    payload += "\"timestamp\":" + String(now);
    payload += "}";
    
    // Publicar
    client.publish(topic_data, payload.c_str(), false);
    Serial.println("Datos publicados: " + payload);
  }
}
```

### Python (Raspberry Pi)

```python
import paho.mqtt.client as mqtt
import json
import time
from datetime import datetime

# Configuración MQTT
MQTT_BROKER = "192.168.1.100"
MQTT_PORT = 1883
MQTT_USER = "device_001"
MQTT_PASSWORD = "secure_password"
MQTT_CLIENT_ID = "RPI_001"

# Topics
TOPIC_DATA = "iot/sensors/RPI_001/data"
TOPIC_COMMANDS = "iot/devices/RPI_001/commands"

def on_connect(client, userdata, flags, rc):
    print(f"Conectado con código: {rc}")
    client.subscribe(TOPIC_COMMANDS)

def on_message(client, userdata, msg):
    print(f"Comando recibido: {msg.payload.decode()}")
    # Procesar comando
    command = json.loads(msg.payload.decode())
    handle_command(command)

def on_disconnect(client, userdata, rc):
    print("Desconectado del broker")
    if rc != 0:
        print("Reconectando...")

# Crear cliente MQTT
client = mqtt.Client(client_id=MQTT_CLIENT_ID)
client.username_pw_set(MQTT_USER, MQTT_PASSWORD)
client.on_connect = on_connect
client.on_message = on_message
client.on_disconnect = on_disconnect

# Conectar al broker
client.connect(MQTT_BROKER, MQTT_PORT, 60)
client.loop_start()

try:
    while True:
        # Leer sensores
        temperature = read_temperature_sensor()
        humidity = read_humidity_sensor()
        
        # Crear payload
        payload = {
            "device_id": "RPI_001",
            "sensors": {
                "temperature": temperature,
                "humidity": humidity
            },
            "timestamp": int(time.time())
        }
        
        # Publicar datos
        client.publish(
            TOPIC_DATA,
            json.dumps(payload),
            qos=1,
            retain=False
        )
        
        print(f"Datos publicados: {payload}")
        time.sleep(60)  # Publicar cada 60 segundos
        
except KeyboardInterrupt:
    print("\nDeteniendo cliente MQTT...")
    client.loop_stop()
    client.disconnect()
```

## Integración con Backend Django

### Procesar Mensajes MQTT

Puedes crear un cliente MQTT en Django para procesar mensajes entrantes:

```python
# apps/mqtt/mqtt_client.py
import paho.mqtt.client as mqtt
import json
from apps.readings.models import Lectura
from apps.devices.models import Dispositivo
from apps.sensors.models import Sensor

def on_message(client, userdata, msg):
    """Procesar mensajes MQTT entrantes"""
    try:
        payload = json.loads(msg.payload.decode())
        device_id = payload.get('device_id')
        
        # Obtener dispositivo
        dispositivo = Dispositivo.objects.get(mqtt_client_id=device_id)
        
        # Crear lecturas
        for sensor_type, valor in payload.get('sensors', {}).items():
            sensor = Sensor.objects.get(
                mqtt_topic_suffix=sensor_type,
                dispositivos=dispositivo
            )
            
            Lectura.objects.create(
                dispositivo=dispositivo,
                sensor=sensor,
                valor=valor,
                mqtt_message_id=str(msg.mid),
                mqtt_qos=msg.qos,
                mqtt_retained=msg.retain
            )
            
        print(f"Lecturas creadas para {device_id}")
        
    except Exception as e:
        print(f"Error procesando mensaje: {e}")
```

## Monitoreo y Debugging

### Ver Estado de Conexiones

```bash
# Desde API
curl http://localhost:8000/api/mqtt/device-status/ \
  -H "Authorization: Bearer <token>"

# Respuesta:
{
  "total_mqtt_devices": 10,
  "online": 8,
  "offline": 2,
  "error": 0,
  "percentage_online": 80.0
}
```

### Dashboard EMQX

Accede al dashboard de EMQX para monitorear:
- http://localhost:18083
- Ver clientes conectados
- Monitor de topics
- Estadísticas en tiempo real
- Logs y debugging

### Logs del Broker

```bash
# Ver logs de EMQX
docker logs emqx -f --tail 100

# Ver logs de Django
docker-compose logs -f backend
```

## Seguridad

### 1. Autenticación

- Usa credenciales únicas por dispositivo
- Rota passwords regularmente
- Considera usar certificados X.509 para producción

### 2. Autorización ACL

Configura ACL en EMQX para limitar acceso:

```
# etc/acl.conf
{allow, {user, "device_001"}, publish, ["iot/sensors/ESP32_001/#"]}.
{allow, {user, "device_001"}, subscribe, ["iot/devices/ESP32_001/#"]}.
{deny, all}.
```

### 3. TLS/SSL

Para producción, usa MQTTS:

```python
# En BrokerConfig
{
    "protocol": "mqtts",
    "port": 8883,
    "use_tls": true,
    "ca_cert": "-----BEGIN CERTIFICATE-----\n..."
}
```

## Troubleshooting

### Error: Connection Refused

```bash
# Verificar que EMQX esté corriendo
docker ps | grep emqx

# Verificar puerto
netstat -an | grep 1883

# Ver logs
docker logs emqx
```

### Error: Unauthorized

- Verificar credenciales en EMQX dashboard
- Verificar que el usuario existe en EMQX
- Revisar configuración ACL

### Error: QoS 2 no funciona

- Verificar que EMQX soporte QoS 2
- Usar QoS 1 para mayor compatibilidad

## Mejores Prácticas

1. **Usar QoS apropiado**: QoS 1 para la mayoría de casos
2. **Publish Interval**: No menos de 1 segundo entre mensajes
3. **Keep-Alive**: 60 segundos es un buen balance
4. **Clean Session**: True para dispositivos IoT móviles
5. **Retain**: Solo para mensajes de estado
6. **Topic Design**: Usar jerarquía lógica
7. **Payload Size**: Mantener mensajes pequeños (<1KB)

## Referencias

- [MQTT.org](https://mqtt.org/) - Especificación MQTT
- [EMQX Documentation](https://docs.emqx.com/) - Documentación EMQX
- [Paho MQTT](https://www.eclipse.org/paho/) - Librerías cliente MQTT
