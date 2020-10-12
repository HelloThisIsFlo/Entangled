from entangled.plex import MockPlexApi
import pytest


@pytest.fixture
def mock_plex_api():
    return MockPlexApi()


class TestMockPlexApiLogsCalls:
    def test_records_call_without_args(self, mock_plex_api: MockPlexApi):
        assert mock_plex_api.mock_calls == []
        mock_plex_api.current_movie_time()
        assert mock_plex_api.mock_calls == ['current_movie_time']

    def test_records_call_with_args(self, mock_plex_api: MockPlexApi):
        assert mock_plex_api.mock_calls == []
        mock_plex_api.seek_to(1, 23, 55)
        assert mock_plex_api.mock_calls == ['seek_to 1 23 55']

    def test_records_multiple_calls(self, mock_plex_api: MockPlexApi):
        assert mock_plex_api.mock_calls == []
        mock_plex_api.current_movie_time()
        mock_plex_api.seek_to(1, 23, 55)
        mock_plex_api.current_movie_time()
        mock_plex_api.current_movie_time()
        assert mock_plex_api.mock_calls == [
            'current_movie_time',
            'seek_to 1 23 55',
            'current_movie_time',
            'current_movie_time',
        ]
