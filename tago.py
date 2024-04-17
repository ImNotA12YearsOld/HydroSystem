import urequests
import ujson

class TagoIO:
    def __init__(self, token):
        self.token = token
        self.endpoint = "https://api.tago.io/data"

    def send_data(self, data):
        headers = {'Content-Type': 'application/json', 'Device-Token': self.token}
        response = urequests.post(self.endpoint, headers=headers, data=ujson.dumps(data))
        return response.status_code == 200
