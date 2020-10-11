import pytest

import entangled.server as server


@pytest.fixture
def app():
    return server.initialize_app('unit_tests')


@pytest.fixture
def client(app):
    app.config['TESTING'] = True

    with app.test_client() as client:
        yield client
