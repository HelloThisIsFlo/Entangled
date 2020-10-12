import pytest
from unittest.mock import patch
from entangled.entangled import Entangled
from entangled.plex import PlexApi
from datetime import datetime
from entangled.config import config


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


def first_arg_of_last_call(mock):
    (args, _kwargs) = mock.call_args
    return args[0]


class TestMqttConnection:
    def test_connects_to_mqtt_on_connect(self, entangled: Entangled, mqtt_client_mock):
        entangled.connect_to_mqtt()
        mqtt_client_mock.connect.assert_called_once()

    @patch('atexit.register')
    def test_registers_disconnect_hook_on_connect(self, atexit_register, entangled: Entangled, mqtt_client_mock):
        entangled.connect_to_mqtt()
        atexit_register.assert_called_once_with(mqtt_client_mock.destroy)

    def test_listens_for_play_message(self, entangled: Entangled, mqtt_client_mock):
        entangled.connect_to_mqtt()
        mqtt_client_mock.listen_for_message.assert_called_once_with(
            entangled._on_play_cmd,
            type='play'
        )


class TestSendPlayCmd:
    def test_sends_mqtt_message(self, entangled: Entangled, mqtt_client_mock):
        entangled.send_play_cmd()
        mqtt_client_mock.send_message.assert_called_once()

    def test_gets_current_movie_time(self, entangled, plex_api_mock: PlexApi):
        entangled.send_play_cmd()
        plex_api_mock.current_movie_time.assert_called_once()

    def test_mqtt_message_contains_type(self, entangled, mqtt_client_mock, plex_api_mock: PlexApi):
        entangled.send_play_cmd()
        msg_sent = first_arg_of_last_call(mqtt_client_mock.send_message)
        assert 'type' in msg_sent
        assert msg_sent['type'] == 'play'

    def test_mqtt_message_contains_current_movie_time(self, entangled, mqtt_client_mock, plex_api_mock: PlexApi):
        MOCK_MOVIE_TIME = "2:27:31"
        plex_api_mock.current_movie_time.return_value = MOCK_MOVIE_TIME
        entangled.send_play_cmd()
        msg_sent = first_arg_of_last_call(mqtt_client_mock.send_message)
        assert 'movieTime' in msg_sent
        assert msg_sent['movieTime'] == MOCK_MOVIE_TIME

    @patch('entangled.entangled.datetime')
    def test_mqtt_message_contains_play_at_time(self, datetime_mock, entangled, plex_api_mock: PlexApi, mqtt_client_mock):
        def timestamp_in_ms(dt):
            return int(dt.timestamp()) * 1000

        config['entangled']['start_delay'] = 5  # 5 secs
        now = datetime.fromisoformat('2020-11-27T13:45:23')
        now_plus_5_sec = datetime.fromisoformat('2020-11-27T13:45:28')
        datetime_mock.now.return_value = now

        entangled.send_play_cmd()

        msg_sent = first_arg_of_last_call(mqtt_client_mock.send_message)
        assert 'playAt' in msg_sent
        assert msg_sent['playAt'] == timestamp_in_ms(now_plus_5_sec)


class TestReceivePlayCmd:
    def test_it_seeks_to_movie_time(self, entangled: Entangled, plex_api_mock: PlexApi):
        entangled._on_play_cmd({
            'type': 'play',
            'movieTime': '1:23:45',
            'playAt': 1602516359362,
        })

        plex_api_mock.seek_to.assert_called_once_with(
            1, 23, 45
        )
