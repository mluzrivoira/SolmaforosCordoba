import json
import random
import time
import paho.mqtt.client as mqtt
import numpy as np
from datetime import datetime
import pytz

# Configuración del broker MQTT
BROKER = "test.mosquitto.org"
PUERTO = 1883
TOPICO = "marialuzrivoira_PI"

# Zona Horaria de Argentina
argentina_tz = pytz.timezone("America/Argentina/Buenos_Aires")

ubicaciones = [
    {"id": 1, "nombre": "Córdoba Capital", "latitud": -31.4201, "longitud": -64.1888},
    {"id": 2, "nombre": "San Francisco", "latitud": -31.4295, "longitud": -62.0849},
    {"id": 3, "nombre": "Río Cuarto", "latitud": -33.1239, "longitud": -64.3490},
    {"id": 4, "nombre": "Villa María", "latitud": -32.4103, "longitud": -63.2434},
    {"id": 5, "nombre": "San Francisco del Chañar", "latitud": -29.7864, "longitud": -63.9417},
    {"id": 6, "nombre": "Huinca Renancó", "latitud": -34.8397, "longitud": -64.3747},
    {"id": 7, "nombre": "Freyre", "latitud": -31.1644, "longitud": -62.0972},
    {"id": 8, "nombre": "San Marcos Sud", "latitud": -32.6282, "longitud": -62.4792},
    {"id": 9, "nombre": "Parque Nacional Traslasierra", "latitud": -31.1634, "longitud": -65.4595},
]

def generar_temperaturas(horas, dias):
    temperaturas = np.zeros((horas, dias))
    for dia in range(dias):
        for hora in range(horas):
            if 10 <= hora < 19:
                temperatura = round(np.random.uniform(25, 40),1)
            else:
                temperatura = round(np.random.uniform(18, 25),1)
            temperaturas[hora, dia] = temperatura
    return temperaturas
temperaturas = generar_temperaturas(24, 31)

def generar_uvs(horas, dias):
    uvs = np.zeros((horas, dias))
    for dia in range(dias):
        for hora in range(horas):
            if 10 <= hora < 19:
                uv = round(np.random.uniform(5, 11),0)
            else:
                uv = round(np.random.uniform(0, 4),0)
            uvs[hora, dia] = uv
    return uvs
uvs = generar_uvs(24, 31)

cliente = mqtt.Client()

def conectar_mqtt():
    try:
        cliente.connect(BROKER, PUERTO, 60)
        cliente.loop_start()
    except OSError as e:
        print(f"Error al conectar con el broker MQTT: {e}")
        return

def generar_datos_simulados(ubicacion, hora_actual=None):
    if not hora_actual:
        hora_actual = datetime.now(argentina_tz)

    hora = hora_actual.hour
    dia_random = random.randint(0, 30)
    datos = {
        "id": ubicacion["id"],
        "ubicacion": ubicacion["nombre"],
        "temperatura": temperaturas[hora, dia_random],
        "uv": uvs[hora, dia_random],
        "latitud": ubicacion["latitud"],
        "longitud": ubicacion["longitud"],
        "fecha_hora": hora_actual.strftime("%Y-%m-%d %H:%M:%S")
    }

    return json.dumps(datos)

def publicar_mqtt(mensaje_json):
    resultado = cliente.publish(TOPICO, mensaje_json)
    if resultado.rc == mqtt.MQTT_ERR_SUCCESS:
        print(f"Publicado en MQTT: {mensaje_json}")
    else:
        print("Error al publicar en MQTT")

# Conectar antes de comenzar
conectar_mqtt()

# Publicar datos de todas las ubicaciones cada 30 minutos
while True:
    hora_actual = datetime.now(argentina_tz)
    for ubicacion in ubicaciones:
        mensaje_json = generar_datos_simulados(ubicacion, hora_actual)
        publicar_mqtt(mensaje_json)
        time.sleep(1)  # Pequeña pausa para evitar publicar todos de golpe (opcional)

    print("Esperando 30 minutos para el próximo envío...\n")
    time.sleep(1800)  # Esperar 30 minutos
