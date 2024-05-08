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
    
#     def format_date_time(self, hora):
#         dia = hora[2]
#         mes = hora[1]
#         ano = hora[0]
#         hora = hora[3]
#         minuto = hora[4]
#         segundo = hora[5]
#         return "{:02d}/{:02d}/{:04d} {:02d}:{:02d}:{:02d}".format(dia, mes, ano, hora, minuto, segundo)

    
    def send_data(self, data):
        client_id = "HydroSystem"  # Pode ser qualquer identificador único
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

