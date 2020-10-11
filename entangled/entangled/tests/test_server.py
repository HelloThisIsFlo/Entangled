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


@patch('entangled.entangled.Entangled')
def test_sends_play_message(EntangledMock, client, app):
    entangled_mock = EntangledMock()
    app.config['ENTANGLED'] = entangled_mock

    client.post('/play')

    entangled_mock.play.assert_called_once()
