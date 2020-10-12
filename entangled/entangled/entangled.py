import atexit
from datetime import datetime
from entangled.mqtt import MQTTClient
from entangled.plex import PlexApi
from entangled.config import config
from entangled.scheduler import schedule_run


def now_timestamp():
    return int(datetime.now().timestamp())


class Entangled:
    def __init__(self, plex_api: PlexApi):
        self.mqtt_client = MQTTClient()
        self.plex_api = plex_api
        start_delay = config['entangled']['start_delay']

    def connect_to_mqtt(self):
        self.mqtt_client.connect()
        atexit.register(self.mqtt_client.destroy)
        self.mqtt_client.listen_for_message(
            self._on_play_cmd,
            type='play'
        )

    def send_play_cmd(self):
        current_movie_time = self.plex_api.current_movie_time()

        start_delay = config['entangled']['start_delay']
        play_at = (now_timestamp() + start_delay) * 1000

        self.mqtt_client.send_message({
            'type': 'play',
            'movieTime': current_movie_time,
            'playAt': play_at
        })

    def _on_play_cmd(self, cmd):
        def movie_time(cmd):
            return tuple(map(
                int,
                cmd['movieTime'].split(':')
            ))

        def play_at_datetime(cmd):
            return datetime.fromtimestamp(cmd['playAt'] / 1000.0)

        self.plex_api.seek_to(*movie_time(cmd))
        schedule_run(
            play_at_datetime(cmd),
            self.plex_api.play
        )
