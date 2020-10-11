import atexit
from entangled.mqtt import MQTTClient
from entangled.plex import PlexApi


class Entangled:
    def __init__(self, plex_api: PlexApi):
        self.mqtt_client = MQTTClient()
        self.plex_api = plex_api

    def connect_to_mqtt(self):
        self.mqtt_client.connect()
        atexit.register(self.mqtt_client.destroy)

    def play(self):
        current_movie_time = self.plex_api.current_movie_time()

        self.mqtt_client.send_message({
            'movieTime': current_movie_time
        })
