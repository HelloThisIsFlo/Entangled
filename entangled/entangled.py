from flask import Flask, render_template
import sys
import atexit

from src.logger import configure_logger
from src.mqtt import MQTTClient
from src.logger import logger


app = Flask(__name__)


mqtt_client = MQTTClient()
mqtt_client.connect()
atexit.register(mqtt_client.destroy)
logger.info('module init')


@app.route('/')
def main_page():
    return render_template('main_page.html', example_var="frank")


@app.route('/play', methods=['POST'])
def play():
    mqtt_client.send_message('play')
    return 'playing'
