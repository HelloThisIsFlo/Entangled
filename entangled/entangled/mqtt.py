import json
import paho.mqtt.client as mqtt
from entangled.config import config
from entangled.logger import logger


class MQTTClient:
    def __init__(self):
        self.topic = config['mqtt']['topic']
        self.paho_client = mqtt.Client(client_id='entangled')
        self.paho_client.on_connect = self._on_connect
        # self.paho_client.on_message = self.on_message

        self.paho_client.username_pw_set(
            config['mqtt']['user'],
            config['mqtt']['pass'])

    def send_message(self, message_as_dict):
        message = json.dumps(message_as_dict)
        self.paho_client.publish(
            self.topic,
            payload=message)

    def connect(self):
        logger.info('Connecting to MQTT')
        self.paho_client.connect(
            host=config['mqtt']['domain'],
            port=config['mqtt']['port'])
        self.paho_client.loop_start()

    def destroy(self):
        logger.info('Disconnecting from MQTT')
        self.paho_client.loop_stop()
        self.paho_client.disconnect()

    @staticmethod
    def _on_connect(client, _userdata, _flags, _rc):
        logger.info('Connected to MQTT')
        # client.subscribe(config['mqtt']['topic'])
        # logger.info(f"Subscribed to {config['mqtt']['topic']}")

    # def on_message(self, _client, _userdata, msg):
    #     command = msg.payload.decode()
    #     logger.info(f"Just received: '{command}' on '{msg.topic}'")
    #     self.cmd_handler(command)
