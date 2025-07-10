
import paho.mqtt.client as mqtt
import json
from .models import Medicion
import django
import time
import threading


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Conectado correctamente al broker MQTT")
        client.subscribe("marialuzrivoira_PI")
    else:
        print(f"Error al conectar: Código {rc}")


# Función para asignar color según índice UV (según la OMS)
def obtener_color_uv(uv):
    if uv <= 2.9:
        return "Verde"
    elif 3 <= uv <= 5.9:
        return "Amarillo"
    elif 6 <= uv <= 7.9:
        return "Naranja"
    elif 8 <= uv <= 10.9:
        return "Rojo"
    else:
        return "Violeta"
ultima_vez = time.time()
tiempo_limite = 2000 # Tiempo en segundos para el watchdog


# Función de callback cuando se recibe un mensaje MQTT
def on_message(client, userdata, msg):
    global ultima_vez
    ultima_vez = time.time()
    mensaje = msg.payload.decode()
    print(f"Mensaje recibido: {mensaje}")
    
    try:
        datos = json.loads(mensaje)
        
        # Extraer los datos recibidos
        ubicacion_id = datos.get("id", 0)
        ubicacion = datos.get("ubicacion", "Desconocida")
        temperatura = datos.get("temperatura", 0.0)
        uv = datos.get("uv", 0.0)
        uv = int(round(uv,0))
        latitud = datos.get("latitud", 0.0)
        longitud = datos.get("longitud", 0.0)

        # Calcular el color según el índice UV
        color_uv = obtener_color_uv(uv)
        
        # Guardar la medición en la base de datos
        medicion = Medicion(
            ubicacion_id=ubicacion_id,
            ubicacion=ubicacion,
            temperatura=temperatura,
            uv=uv,
            latitud=latitud,
            longitud=longitud,
            color_uv=color_uv,  # Guardar el color calculado
        )
        medicion.save()
        
        print("Medición guardada en la base de datos")
    
    except json.JSONDecodeError:
        print("Error al decodificar el mensaje JSON")


client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message
client.connect("test.mosquitto.org", 1883, 60)

def watchdog():
    while True:
        ahora = time.time()
        if ahora - ultima_vez > tiempo_limite:
            alerta = {
                "tipo": "alerta",
                "mensaje": f"No se reciben datos desde hace {int(ahora - ultima_vez)} segundos"
            }
            client.publish("solmaforos/control", json.dumps(alerta))
            print("Alerta enviada:", alerta)
            time.sleep(tiempo_limite)  # Evitar spam
        time.sleep(5)
threading.Thread(target=watchdog, daemon=True).start()


client.loop_start()
