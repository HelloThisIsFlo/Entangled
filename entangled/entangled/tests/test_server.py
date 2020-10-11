from unittest.mock import patch
from unittest.mock import Mock
import pytest


@patch('entangled.server.render_template')
def test_renders_the_main_page(render_template_mock, client):
    MOCK_HTML = 'Main Page HTML'
    render_template_mock.return_value = MOCK_HTML

    resp = client.get('/')

    render_template_mock.assert_called_once_with('main_page.html')
    assert resp.data.decode() == MOCK_HTML


class TestPlay:
    @patch('entangled.mqtt.MQTTClient')
    def test_sends_play_message(self, MQTTClientMock, client, app):
        mqtt_client_mock = MQTTClientMock()
        app.config['MQTT_CLIENT'] = mqtt_client_mock

        client.post('/play')

        mqtt_client_mock.send_message.assert_called_once_with('play')

    def test_gets_current_movie_time(self):
        # later
        pass
