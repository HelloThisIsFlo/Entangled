import abc
import os
import functools

from entangled.logger import logger
from plexapi.myplex import MyPlexAccount
from plexapi.client import PlexClient


class PlexApi(abc.ABC):
    @abc.abstractmethod
    def current_movie_time(self):
        pass

    @abc.abstractmethod
    def seek_to(self, hour, minute, second):
        pass

    @abc.abstractmethod
    def play(self):
        pass


def record_mock_call(func):
    @functools.wraps(func)
    def func_with_logging(self, *args, **kwargs):
        if args:
            formatted_mock_call = f"{func.__name__} {' '.join(map(str, args))}"
        else:
            formatted_mock_call = f"{func.__name__}"

        self.mock_calls.append(formatted_mock_call)
        return func(self, *args, **kwargs)

    return func_with_logging


class MockPlexApi(PlexApi):
    def __init__(self):
        self.mock_current_movie_time = ''
        self.mock_calls = []

    @record_mock_call
    def current_movie_time(self):
        return self.mock_current_movie_time

    @record_mock_call
    def seek_to(self, hour, minute, second):
        pass

    @record_mock_call
    def play(self):
        pass


def ensure_connected_to_account(func):
    @functools.wraps(func)
    def func_with_check(self, *args, **kwargs):
        if not self.account:
            raise RuntimeError(
                f"Not connected to the account! Make sure to connect before calling this function: '{func.__name__}'")
        return func(self, *args, **kwargs)

    return func_with_check


def ensure_connected_to_resource(func):
    @functools.wraps(func)
    def func_with_check(self, *args, **kwargs):
        if not self.resource:
            raise RuntimeError(
                f"Not connected to the player! Make sure to connect before calling this function: '{func.__name__}'")
        return func(self, *args, **kwargs)

    return func_with_check


class PythonLibPlexApi(PlexApi):
    # TODO
    # Add a 'connect_to_account' and 'connect_to_resource' method
    # and call them both in 'Entangled' (test via outside-in testing
    # that it's been call during 'Entangled' '__init__')
    # Then in the 'list_all_resources' script, only call 'connect_to_account'
    # Boom lifecyle problem solved, and it's transparent to the higher level
    # using 'Entangled'
    def __init__(self) -> None:
        self.username = os.environ['PLEX_USER']
        self.password = os.environ['PLEX_PASS']
        self.resource_name = os.environ['PLEX_RESOURCE']
        self._connect_to_resource()

    def _connect_to_resource(self):
        self.account = MyPlexAccount(self.username, self.password)
        if (self.resource_name):
            self.resource = self.account.resource(self.resource_name).connect()
        else:
            logger.info("DEBUG TEMP: Add resource to envvar")

    @ensure_connected_to_account
    def all_resources(self):
        return self.account.resources()

    @ensure_connected_to_resource
    def current_movie_time(self):
        logger.info('Getting current movie time')
        # TODO: Fix 'self.resource.timeline.time' can be None sometimes if the movie was paused. Find solution.
        print(self.resource.timeline.time)
        import math
        timestamp = math.floor(self.resource.timeline.time / 1000)
        hours = math.floor(timestamp/3600)
        min = math.floor(timestamp / 60) - hours * 60
        secs = timestamp - hours*3600 - min*60
        current_time = f"{hours}:{min:02}:{secs:02}"
        return current_time

    @ensure_connected_to_resource
    def seek_to(self, hour, minute, second):
        logger.info(f"Seeking to: '{hour}:{minute}:{second}")

        def seconds(seconds_num):
            return seconds_num * 1000

        def minutes(minutes_num):
            return seconds(minutes_num * 60)

        def hours(hours_num):
            return minutes(hours_num * 60)

        self.resource.seekTo(
            hours(hour) + minutes(minute) + seconds(second)
        )

    @ensure_connected_to_resource
    def play(self):
        logger.info('Playing')
        self.resource.play()
