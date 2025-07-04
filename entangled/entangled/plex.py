import abc
import os
import functools
import logging

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

    @abc.abstractmethod
    def pause(self):
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

    @record_mock_call
    def pause(self):
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


class PlexConnectionError(Exception):
    """Custom exception for Plex connection issues"""
    pass


class PythonLibPlexApi(PlexApi):
    def __init__(self) -> None:
        self.username = os.environ['PLEX_USER']
        self.password = os.environ['PLEX_PASS']
        self.resource_name = os.environ.get('PLEX_RESOURCE', '')
        self.account = None
        self.resource = None
        self.connect_to_account()
        if self.resource_name:
            self.connect_to_resource()
        else:
            logger.warning("No PLEX_RESOURCE specified. Call connect_to_resource() after setting resource name.")

    def connect_to_account(self):
        """Connect to Plex account using credentials"""
        try:
            logger.info(f"Connecting to Plex account for user: {self.username}")
            self.account = MyPlexAccount(self.username, self.password)
            logger.info("Successfully connected to Plex account")
        except Exception as e:
            logger.error(f"Failed to connect to Plex account: {e}")
            raise PlexConnectionError(f"Failed to connect to Plex account: {e}")

    def connect_to_resource(self, resource_name=None):
        """Connect to a specific Plex resource/client"""
        if not self.account:
            raise PlexConnectionError("Must connect to account before connecting to resource")
        
        target_resource = resource_name or self.resource_name
        if not target_resource:
            raise PlexConnectionError("No resource name specified")
        
        try:
            logger.info(f"Connecting to Plex resource: {target_resource}")
            plex_resource = self.account.resource(target_resource)
            self.resource = plex_resource.connect()
            self.resource_name = target_resource
            logger.info(f"Successfully connected to Plex resource: {target_resource}")
        except Exception as e:
            logger.error(f"Failed to connect to Plex resource '{target_resource}': {e}")
            raise PlexConnectionError(f"Failed to connect to Plex resource '{target_resource}': {e}")

    @ensure_connected_to_account
    def all_resources(self):
        """Get all available Plex resources"""
        try:
            return self.account.resources()
        except Exception as e:
            logger.error(f"Failed to get Plex resources: {e}")
            raise PlexConnectionError(f"Failed to get Plex resources: {e}")

    @ensure_connected_to_resource
    def current_movie_time(self):
        """Get current movie time with proper error handling"""
        logger.info('Getting current movie time')
        
        try:
            # Refresh timeline to get current state
            self.resource.timeline()
            
            # Check if timeline.time is None (movie is paused or stopped)
            if self.resource.timeline.time is None:
                logger.warning("Timeline time is None - media may be paused or stopped")
                # Return last known position or 0:00:00 if not available
                if hasattr(self.resource.timeline, 'offset') and self.resource.timeline.offset:
                    timestamp = self.resource.timeline.offset // 1000
                else:
                    logger.warning("No timeline offset available, returning 0:00:00")
                    return "0:00:00"
            else:
                timestamp = self.resource.timeline.time // 1000
            
            # Convert milliseconds to readable time format
            hours = timestamp // 3600
            minutes = (timestamp % 3600) // 60
            seconds = timestamp % 60
            
            current_time = f"{hours}:{minutes:02d}:{seconds:02d}"
            logger.info(f"Current movie time: {current_time}")
            return current_time
            
        except Exception as e:
            logger.error(f"Failed to get current movie time: {e}")
            raise PlexConnectionError(f"Failed to get current movie time: {e}")

    @ensure_connected_to_resource
    def seek_to(self, hour, minute, second):
        """Seek to specific time position"""
        logger.info(f"Seeking to: {hour}:{minute:02d}:{second:02d}")

        def seconds_to_ms(seconds_num):
            return seconds_num * 1000

        def minutes_to_ms(minutes_num):
            return seconds_to_ms(minutes_num * 60)

        def hours_to_ms(hours_num):
            return minutes_to_ms(hours_num * 60)

        try:
            seek_time_ms = hours_to_ms(hour) + minutes_to_ms(minute) + seconds_to_ms(second)
            self.resource.seekTo(seek_time_ms)
            logger.info(f"Successfully seeked to {hour}:{minute:02d}:{second:02d}")
        except Exception as e:
            logger.error(f"Failed to seek to {hour}:{minute:02d}:{second:02d}: {e}")
            raise PlexConnectionError(f"Failed to seek: {e}")

    @ensure_connected_to_resource
    def play(self):
        """Start/resume playback"""
        logger.info('Starting playback')
        try:
            self.resource.play()
            logger.info('Playback started successfully')
        except Exception as e:
            logger.error(f"Failed to start playback: {e}")
            raise PlexConnectionError(f"Failed to start playback: {e}")

    @ensure_connected_to_resource
    def pause(self):
        """Pause playback"""
        logger.info('Pausing playback')
        try:
            self.resource.pause()
            logger.info('Playback paused successfully')
        except Exception as e:
            logger.error(f"Failed to pause playback: {e}")
            raise PlexConnectionError(f"Failed to pause playback: {e}")

    def is_connected(self):
        """Check if connected to both account and resource"""
        return self.account is not None and self.resource is not None

    def disconnect(self):
        """Clean up connections"""
        logger.info("Disconnecting from Plex")
        self.resource = None
        self.account = None
