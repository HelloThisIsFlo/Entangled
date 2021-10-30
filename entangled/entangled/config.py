from pathlib import Path
import yaml
import os


def seconds(seconds_num):
    return seconds_num


def minutes(minutes_num):
    return seconds(minutes_num * 60)


config = {
    'mqtt': {
        'user': os.environ['MQTT_USER'],
        'pass': os.environ['MQTT_PASS'],
        'domain': 'floriankempenich.com',
        'port': 6789,
        'topic': 'entangled',
        'client-id': 'entangled-florian',
        'use-ssl': True
    },
    'entangled': {
        'start_delay': seconds(30)
    },
}


class Config:
    def __init__(self, config_file_path="~/.entangled"):
        self.config = self._load_config(config_file_path)

    @staticmethod
    def _load_config(config_file_path):
        if not Path(config_file_path).exists():
            raise RuntimeError(
                f"Config file was not found | Path='{config_file_path}'")

        with open(config_file_path) as config_file:
            return yaml.safe_load(config_file.read())

    def __getitem__(self, key):
        return self.config[key]
