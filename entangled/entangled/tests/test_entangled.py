
# Todo:
# - test that it connects on connect
# - test that it registers disconnect hook on connect

import pytest
from unittest.mock import patch
from entangled.entangled import Entangled
from entangled.plex import PlexApi


@pytest.fixture
def mqtt_client_mock():
    with patch('entangled.entangled.MQTTClient') as MQTTClientMock:
        yield MQTTClientMock()


@pytest.fixture
def plex_api_mock():
    with patch('entangled.plex.PlexApi') as PlexApiMock:
        yield PlexApiMock()


@pytest.fixture
def entangled(mqtt_client_mock, plex_api_mock):
    return Entangled(plex_api_mock)


def test_connects_to_mqtt_on_connect(entangled: Entangled, mqtt_client_mock):
    entangled.connect_to_mqtt()
    mqtt_client_mock.connect.assert_called_once()


@patch('atexit.register')
def test_registers_disconnect_hook_on_connect(atexit_register, entangled: Entangled, mqtt_client_mock):
    entangled.connect_to_mqtt()
    atexit_register.assert_called_once_with(mqtt_client_mock.destroy)


def first_arg_of_last_call(mock):
    (args, _kwargs) = mock.call_args
    return args[0]


class TestSendPlayMessageOnPlay:
    def test_sends_mqtt_message(self, entangled: Entangled, mqtt_client_mock):
        entangled.play()
        mqtt_client_mock.send_message.assert_called_once()

    def test_gets_current_movie_time(self, entangled, plex_api_mock: PlexApi):
        entangled.play()
        plex_api_mock.current_movie_time.assert_called_once()

    def test_mqtt_message_contains_current_movie_time(self, entangled, mqtt_client_mock, plex_api_mock: PlexApi):
        MOCK_MOVIE_TIME = "2:27"
        plex_api_mock.current_movie_time.return_value = MOCK_MOVIE_TIME
        entangled.play()
        msg_sent = first_arg_of_last_call(mqtt_client_mock.send_message)
        assert 'movieTime' in msg_sent
        assert msg_sent['movieTime'] == MOCK_MOVIE_TIME
