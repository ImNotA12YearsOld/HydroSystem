# tago.py

import json
from simple import MQTTClient
import utime
import ntptime

class TagoIO:
    def __init__(self, mqtt_host, mqtt_port, mqtt_username, mqtt_password, device_token):
        self.mqtt_host = mqtt_host
        self.mqtt_port = mqtt_port
        self.mqtt_username = mqtt_username
        self.mqtt_password = mqtt_password
        self.device_token = device_token
        self.mqtt_topic = "tago/data/post"
        
    def send_data(self, data):
        client_id = "HydroSystem - PoC"  # Pode ser qualquer identificador único
        client = MQTTClient(client_id, self.mqtt_host, self.mqtt_port, self.mqtt_username, self.mqtt_password)

        try:
            client.connect()
            payload = json.dumps(data)
            client.publish(self.mqtt_topic, payload)
            print("Dados enviados com sucesso para TagoIO")
        except Exception as e:
            print("Erro ao enviar dados para TagoIO:", e)
        finally:
            client.disconnect()

