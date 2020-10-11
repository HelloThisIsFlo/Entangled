
# Todo:
# - test that it connects on connect
# - test that it registers disconnect hook on connect

import pytest
from unittest.mock import patch
from entangled.entangled import Entangled


@pytest.fixture
def mqtt_client_mock():
    with patch('entangled.entangled.MQTTClient') as MQTTClientMock:
        yield MQTTClientMock()


@pytest.fixture
def entangled(mqtt_client_mock):
    return Entangled()


def test_connects_to_mqtt_on_connect(entangled: Entangled, mqtt_client_mock):
    entangled.connect_to_mqtt()
    mqtt_client_mock.connect.assert_called_once()


@patch('atexit.register')
def test_registers_disconnect_hook_on_connect(atexit_register, entangled: Entangled, mqtt_client_mock):
    entangled.connect_to_mqtt()
    atexit_register.assert_called_once_with(mqtt_client_mock.destroy)


def test_sends_play_message_on_play(entangled: Entangled, mqtt_client_mock):
    entangled.play()
    mqtt_client_mock.send_message.assert_called_once_with('play')
