from django.apps import AppConfig
import threading

class ProyectowebappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'proyectowebapp'

    def ready(self):
        try:
            from . import mqtt_client  # Importa aquí para evitar problemas de inicialización
            print("Iniciando cliente MQTT...")  # Verificación para la consola
            threading.Thread(target=mqtt_client.client.loop_start, daemon=True).start()
        except Exception as e:
            print(f"Error al iniciar el cliente MQTT: {e}")
    