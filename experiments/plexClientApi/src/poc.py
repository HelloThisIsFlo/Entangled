from plexapi.myplex import MyPlexAccount
from plexapi.client import PlexClient
from time import sleep
import requests
from base64 import b64encode

from requests import Session


def load_password():
    with open('./plex_pass') as pass_file:
        return pass_file.read()


class EntangledPOC:
    def __init__(self):
        username = 'shockn745@gmail.com'
        password = load_password()
        self.account = MyPlexAccount(username, password)
        self.resource: PlexClient = None

    def list_resources(self):
        resources = self.account.resources()
        print(resources)

    def connect_to(self, resource_name):
        self.resource = self.account.resource(resource_name).connect()

    def play(self):
        if not self.resource:
            return
        self.resource.play()

    def pause(self):
        if not self.resource:
            return
        self.resource.pause()

    def go_to_10_min_in_movie(self):
        ten_minutes_ms = 10 * 60 * 1000
        self.resource.seekTo(ten_minutes_ms)


def pause_then_play():
    entangled = EntangledPOC()
    entangled.list_resources()
    # return
    entangled.connect_to('TheMacbookPro')
    duration = int(input('How long to pause for: '))
    entangled.pause()
    entangled.go_to_10_min_in_movie()
    sleep(duration)
    entangled.play()



pause_then_play()