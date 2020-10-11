from unittest.mock import patch


@patch('entangled.render_template')
def test_hey(render_template_mock, client):
    render_template_mock.return_value = 'hey'
    resp = client.get('/')

    assert resp.data == b'hey'
