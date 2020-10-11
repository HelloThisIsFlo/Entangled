import os
import tempfile

import pytest

import entangled


@pytest.fixture
def client():
    entangled.app.config['TESTING'] = True

    with entangled.app.test_client() as client:
        yield client
