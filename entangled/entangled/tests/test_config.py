from io import TextIOWrapper
from pathlib import PosixPath
from unittest.mock import MagicMock
import pytest
from entangled.config import Config
from textwrap import dedent
from unittest.mock import patch


@patch.object(Config, '_load_config')
def test_it_loads_config_file_from_home_dir_by_default(_load_config_mock):
    _config = Config()
    _load_config_mock.assert_called_once_with("~/.entangled")


def test_it_throw_informative_error_if_config_file_not_found():
    with pytest.raises(RuntimeError) as error:
        Config(config_file_path="a_file_that_does_not_exist.yaml")
    assert ("Config file was not found | Path='a_file_that_does_not_exist.yaml'"
            in str(error.value))


@pytest.fixture
def mock_config_path(tmp_path):
    mock_config_path = tmp_path / 'mock_config.yaml'
    return mock_config_path


def test_it_loads_configuration_from_file(mock_config_path):
    write_mock_config_to(
        mock_config_path,
        dedent("""
            entangled:
                start_delay: 1111
            mqtt:
                user: MQTT_USER
                pass: MQTT_PASS
                host: MQTT_HOST
                port: 2222
                topic: MQTT_TOPIC
                client-id: MQTT_CLIENT_ID
        """)
    )

    config = Config(config_file_path=mock_config_path)

    assert config['entangled']['start_delay'] == 1111
    assert config['mqtt']['user'] == 'MQTT_USER'
    assert config['mqtt']['pass'] == 'MQTT_PASS'
    assert config['mqtt']['host'] == 'MQTT_HOST'
    assert config['mqtt']['port'] == 2222
    assert config['mqtt']['topic'] == 'MQTT_TOPIC'
    assert config['mqtt']['client-id'] == 'MQTT_CLIENT_ID'


def write_mock_config_to(mock_config_path, mock_config):
    with open(mock_config_path, 'w') as mock_config_file:
        mock_config_file.write(mock_config)
