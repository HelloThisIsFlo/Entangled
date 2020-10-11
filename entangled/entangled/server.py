from flask import Flask, render_template
import sys
import atexit

from entangled.mqtt import MQTTClient
from entangled.logger import logger


def initialize_app():
    app = Flask(
        __name__,
        template_folder='../templates'
    )

    mqtt_client = MQTTClient()
    mqtt_client.connect()
    atexit.register(mqtt_client.destroy)
    logger.info('module init')

    @app.route('/')
    def main_page():
        return render_template('main_page.html')

    @app.route('/play', methods=['POST'])
    def play():
        print(MQTTClient)
        print(MQTTClient())
        mqtt_client.send_message('play')
        return 'playing'

    return app