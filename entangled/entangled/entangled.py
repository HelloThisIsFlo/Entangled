import atexit
from entangled.mqtt import MQTTClient


class Entangled:
    def __init__(self):
        self.mqtt_client = MQTTClient()

    def connect_to_mqtt(self):
        self.mqtt_client.connect()
        atexit.register(self.mqtt_client.destroy)

    def play(self):
        self.mqtt_client.send_message('play')
