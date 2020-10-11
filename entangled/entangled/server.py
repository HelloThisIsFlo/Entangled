from flask import Flask, render_template
import sys
import atexit

from entangled.mqtt import MQTTClient
from entangled.logger import logger


ENVS = [
    'prod',
    'e2e_tests',
    'unit_tests'
]


def initialize_app(env):
    def initialize_deps():
        if env == 'prod':
            mqtt_client = app.config['MQTT_CLIENT']
            mqtt_client.connect()
            atexit.register(mqtt_client.destroy)

    if env not in ENVS:
        raise ValueError(f"Invalid env name: '{env}'")

    app = Flask(__name__, template_folder='../templates')
    app.config['MQTT_CLIENT'] = MQTTClient()

    initialize_deps()

    @app.route('/')
    def main_page():
        return render_template('main_page.html')

    @app.route('/play', methods=['POST'])
    def play():
        app.config['MQTT_CLIENT'].send_message('play')
        return 'playing'

    return app
