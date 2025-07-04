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
        # Check that listen_for_message was called 3 times (play, pause, resume)
        assert mqtt_client_mock.listen_for_message.call_count == 3
        
        # Check the calls individually
        calls = mqtt_client_mock.listen_for_message.call_args_list
        
        # Play message listener
        assert calls[0][0][0] == entangled._on_play_cmd
        assert calls[0][1]['type'] == 'play'
        
        # Pause message listener  
        assert calls[1][0][0] == entangled._on_pause_cmd
        assert calls[1][1]['type'] == 'pause'
        
        # Resume message listener
        assert calls[2][0][0] == entangled._on_resume_cmd
        assert calls[2][1]['type'] == 'resume'


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


class TestSendPauseCmd:
    def test_sends_mqtt_message(self, entangled: Entangled, mqtt_client_mock):
        entangled.send_pause_cmd()
        mqtt_client_mock.send_message.assert_called_once()

    def test_gets_current_movie_time(self, entangled, plex_api_mock: PlexApi):
        entangled.send_pause_cmd()
        plex_api_mock.current_movie_time.assert_called_once()

    def test_mqtt_message_contains_type(self, entangled, mqtt_client_mock, plex_api_mock: PlexApi):
        entangled.send_pause_cmd()
        msg_sent = first_arg_of_last_call(mqtt_client_mock.send_message)
        assert 'type' in msg_sent
        assert msg_sent['type'] == 'pause'

    def test_mqtt_message_contains_current_movie_time(self, entangled, mqtt_client_mock, plex_api_mock: PlexApi):
        MOCK_MOVIE_TIME = "1:15:42"
        plex_api_mock.current_movie_time.return_value = MOCK_MOVIE_TIME
        entangled.send_pause_cmd()
        msg_sent = first_arg_of_last_call(mqtt_client_mock.send_message)
        assert 'movieTime' in msg_sent
        assert msg_sent['movieTime'] == MOCK_MOVIE_TIME

    @patch('entangled.entangled.datetime')
    def test_mqtt_message_contains_pause_at_time(self, datetime_mock, entangled, plex_api_mock: PlexApi, mqtt_client_mock):
        def timestamp_in_ms(dt):
            return int(dt.timestamp()) * 1000

        config['entangled']['start_delay'] = 3  # 3 secs
        now = datetime.fromisoformat('2020-11-27T14:30:15')
        now_plus_3_sec = datetime.fromisoformat('2020-11-27T14:30:18')
        datetime_mock.now.return_value = now

        entangled.send_pause_cmd()

        msg_sent = first_arg_of_last_call(mqtt_client_mock.send_message)
        assert 'pauseAt' in msg_sent
        assert msg_sent['pauseAt'] == timestamp_in_ms(now_plus_3_sec)


class TestSendResumeCmd:
    def test_sends_mqtt_message(self, entangled: Entangled, mqtt_client_mock):
        entangled.send_resume_cmd()
        mqtt_client_mock.send_message.assert_called_once()

    def test_gets_current_movie_time(self, entangled, plex_api_mock: PlexApi):
        entangled.send_resume_cmd()
        plex_api_mock.current_movie_time.assert_called_once()

    def test_mqtt_message_contains_type(self, entangled, mqtt_client_mock, plex_api_mock: PlexApi):
        entangled.send_resume_cmd()
        msg_sent = first_arg_of_last_call(mqtt_client_mock.send_message)
        assert 'type' in msg_sent
        assert msg_sent['type'] == 'resume'

    def test_mqtt_message_contains_current_movie_time(self, entangled, mqtt_client_mock, plex_api_mock: PlexApi):
        MOCK_MOVIE_TIME = "0:45:20"
        plex_api_mock.current_movie_time.return_value = MOCK_MOVIE_TIME
        entangled.send_resume_cmd()
        msg_sent = first_arg_of_last_call(mqtt_client_mock.send_message)
        assert 'movieTime' in msg_sent
        assert msg_sent['movieTime'] == MOCK_MOVIE_TIME

    @patch('entangled.entangled.datetime')
    def test_mqtt_message_contains_resume_at_time(self, datetime_mock, entangled, plex_api_mock: PlexApi, mqtt_client_mock):
        def timestamp_in_ms(dt):
            return int(dt.timestamp()) * 1000

        config['entangled']['start_delay'] = 2  # 2 secs
        now = datetime.fromisoformat('2020-11-27T16:20:45')
        now_plus_2_sec = datetime.fromisoformat('2020-11-27T16:20:47')
        datetime_mock.now.return_value = now

        entangled.send_resume_cmd()

        msg_sent = first_arg_of_last_call(mqtt_client_mock.send_message)
        assert 'resumeAt' in msg_sent
        assert msg_sent['resumeAt'] == timestamp_in_ms(now_plus_2_sec)


class TestReceivePlayCmd:
    @patch('entangled.entangled.schedule_run')
    def test_it_seeks_to_movie_time(self, schedule_run_mock, entangled: Entangled, plex_api_mock: PlexApi):
        entangled._on_play_cmd({
            'type': 'play',
            'movieTime': '1:23:45',
            'playAt': 1602516359362,
        })

        plex_api_mock.seek_to.assert_called_once_with(
            1, 23, 45
        )

    @patch('entangled.entangled.schedule_run')
    def test_it_schedules_a_play_call_at_correct_time(self, schedule_run_mock, entangled: Entangled, plex_api_mock: PlexApi):
        play_at_datetime = datetime.fromisoformat('2020-11-27T13:45:23')
        play_at_timestamp_ms = 1606484723000

        entangled._on_play_cmd({
            'type': 'play',
            'movieTime': '1:23:45',
            'playAt': play_at_timestamp_ms,
        })

        schedule_run_mock.assert_called_once_with(
            play_at_datetime,
            plex_api_mock.play
        )


class TestReceivePauseCmd:
    @patch('entangled.entangled.schedule_run')
    def test_it_seeks_to_movie_time(self, schedule_run_mock, entangled: Entangled, plex_api_mock: PlexApi):
        entangled._on_pause_cmd({
            'type': 'pause',
            'movieTime': '2:10:30',
            'pauseAt': 1602516359362,
        })

        plex_api_mock.seek_to.assert_called_once_with(
            2, 10, 30
        )

    @patch('entangled.entangled.schedule_run')
    def test_it_schedules_a_pause_call_at_correct_time(self, schedule_run_mock, entangled: Entangled, plex_api_mock: PlexApi):
        pause_at_datetime = datetime.fromisoformat('2020-11-27T14:30:15')
        pause_at_timestamp_ms = 1606487415000

        entangled._on_pause_cmd({
            'type': 'pause',
            'movieTime': '2:10:30',
            'pauseAt': pause_at_timestamp_ms,
        })

        schedule_run_mock.assert_called_once_with(
            pause_at_datetime,
            plex_api_mock.pause
        )


class TestReceiveResumeCmd:
    @patch('entangled.entangled.schedule_run')
    def test_it_seeks_to_movie_time(self, schedule_run_mock, entangled: Entangled, plex_api_mock: PlexApi):
        entangled._on_resume_cmd({
            'type': 'resume',
            'movieTime': '0:45:12',
            'resumeAt': 1602516359362,
        })

        plex_api_mock.seek_to.assert_called_once_with(
            0, 45, 12
        )

    @patch('entangled.entangled.schedule_run')
    def test_it_schedules_a_resume_call_at_correct_time(self, schedule_run_mock, entangled: Entangled, plex_api_mock: PlexApi):
        resume_at_datetime = datetime.fromisoformat('2020-11-27T16:20:45')
        resume_at_timestamp_ms = 1606494045000

        entangled._on_resume_cmd({
            'type': 'resume',
            'movieTime': '0:45:12',
            'resumeAt': resume_at_timestamp_ms,
        })

        schedule_run_mock.assert_called_once_with(
            resume_at_datetime,
            plex_api_mock.play  # Resume uses play method
        )
