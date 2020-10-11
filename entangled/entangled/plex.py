import abc


class PlexApi(abc.ABC):
    @abc.abstractmethod
    def current_movie_time(self):
        pass


class MockPlexApi(PlexApi):
    def __init__(self):
        self.mock_current_movie_time = ''

    def current_movie_time(self):
        return self.mock_current_movie_time

class PythonLibPlexApi(PlexApi):
    def current_movie_time(self):
        raise NotImplementedError()
