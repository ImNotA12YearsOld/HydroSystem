import time
import network

class WiFiConfig:
    def __init__(self, ssid, password):
        self.ssid = ssid
        self.password = password
        self.wlan = network.WLAN(network.STA_IF)

    def connect(self):
        if not self.wlan.isconnected():
            print("Conectando ao WiFi...")
            self.wlan.active(True)
            self.wlan.connect(self.ssid, self.password)
            while not self.wlan.isconnected():
                time.sleep(1)
            print("Conectado ao WiFi:", self.ssid)
            print("Endereço IP:", self.wlan.ifconfig()[0])
        else:
            print("Já conectado ao WiFi:", self.ssid)
            print("Endereço IP:", self.wlan.ifconfig()[0])

    def disconnect(self):
        if self.wlan.isconnected():
            print("Desconectando do WiFi...")
            self.wlan.disconnect()
            print("Desconectado do WiFi:", self.ssid)
        else:
            print("Não há conexão WiFi para desconectar.")
