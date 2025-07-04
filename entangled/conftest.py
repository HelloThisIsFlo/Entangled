import os
import pytest
from pathlib import Path

# Load environment variables from .env file before importing other modules
env_file = Path(__file__).parent / '.env'
if env_file.exists():
    with open(env_file) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value

import entangled.server as server


@pytest.fixture
def app():
    return server.initialize_app('unit_tests')


@pytest.fixture
def client(app):
    app.config['TESTING'] = True

    with app.test_client() as client:
        yield client
