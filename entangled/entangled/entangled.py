import atexit
from datetime import datetime
from entangled.mqtt import MQTTClient
from entangled.plex import PlexApi
from entangled.config import config
from entangled.scheduler import schedule_run
from entangled.logger import logger


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
        self.mqtt_client.listen_for_message(
            self._on_pause_cmd,
            type='pause'
        )
        self.mqtt_client.listen_for_message(
            self._on_resume_cmd,
            type='resume'
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

    def send_pause_cmd(self):
        """Send pause command to all clients"""
        current_movie_time = self.plex_api.current_movie_time()
        
        start_delay = config['entangled']['start_delay']
        pause_at = (now_timestamp() + start_delay) * 1000

        self.mqtt_client.send_message({
            'type': 'pause',
            'movieTime': current_movie_time,
            'pauseAt': pause_at
        })

    def send_resume_cmd(self):
        """Send resume command to all clients"""
        current_movie_time = self.plex_api.current_movie_time()
        
        start_delay = config['entangled']['start_delay']
        resume_at = (now_timestamp() + start_delay) * 1000

        self.mqtt_client.send_message({
            'type': 'resume',
            'movieTime': current_movie_time,
            'resumeAt': resume_at
        })

    def _on_play_cmd(self, cmd):
        """Handle incoming play command"""
        logger.info(f"Received play command: {cmd}")
        
        def movie_time(cmd):
            return tuple(map(
                int,
                cmd['movieTime'].split(':')
            ))

        def play_at_datetime(cmd):
            return datetime.fromtimestamp(cmd['playAt'] / 1000.0)

        # Seek to the specified time
        self.plex_api.seek_to(*movie_time(cmd))
        
        # Schedule the play command
        schedule_run(
            play_at_datetime(cmd),
            self.plex_api.play
        )

    def _on_pause_cmd(self, cmd):
        """Handle incoming pause command"""
        logger.info(f"Received pause command: {cmd}")
        
        def movie_time(cmd):
            return tuple(map(
                int,
                cmd['movieTime'].split(':')
            ))

        def pause_at_datetime(cmd):
            return datetime.fromtimestamp(cmd['pauseAt'] / 1000.0)

        # Seek to the specified time
        self.plex_api.seek_to(*movie_time(cmd))
        
        # Schedule the pause command
        schedule_run(
            pause_at_datetime(cmd),
            self.plex_api.pause
        )

    def _on_resume_cmd(self, cmd):
        """Handle incoming resume command"""
        logger.info(f"Received resume command: {cmd}")
        
        def movie_time(cmd):
            return tuple(map(
                int,
                cmd['movieTime'].split(':')
            ))

        def resume_at_datetime(cmd):
            return datetime.fromtimestamp(cmd['resumeAt'] / 1000.0)

        # Seek to the specified time
        self.plex_api.seek_to(*movie_time(cmd))
        
        # Schedule the resume (play) command
        schedule_run(
            resume_at_datetime(cmd),
            self.plex_api.play
        )
