import json
import paho.mqtt.client as mqtt
from entangled.config import config
from entangled.logger import logger
from typing import NamedTuple, Callable


class MsgListener(NamedTuple):
    msg_type: str
    on_message_callback: Callable[[dict], None]


class MQTTClient:
    msg_listeners: [MsgListener]

    def __init__(self):
        self.topic = config['mqtt']['topic']
        self.msg_listeners = []

        self.paho_client = mqtt.Client(client_id=config['mqtt']['client-id'])
        self.paho_client.username_pw_set(
            config['mqtt']['user'],
            config['mqtt']['pass'])
        self.paho_client.on_connect = self._on_connect
        self.paho_client.on_message = self._on_message
        self.paho_client.tls_set(ca_certs='/etc/ssl/cert.pem')

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

    def listen_for_message(self, on_message_callback, type):
        self.msg_listeners.append(
            MsgListener(
                msg_type=type,
                on_message_callback=on_message_callback
            )
        )

    def _on_connect(self, client, _userdata, _flags, _rc):
        logger.info('Connected to MQTT')
        client.subscribe(self.topic)
        logger.info(f"Subscribed to {self.topic}")

    def _on_message(self, _client, _userdata, raw_msg):
        msg = json.loads(raw_msg.payload.decode())
        logger.info(f"Just received: '{msg}'")
        for listener in self.msg_listeners:
            if msg['type'] == listener.msg_type:
                listener.on_message_callback(msg)
