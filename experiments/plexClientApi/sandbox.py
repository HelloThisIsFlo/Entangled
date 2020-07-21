from plexapi.myplex import MyPlexAccount
from plexapi.client import PlexClient
from time import sleep
import requests
from base64 import b64encode


def load_password():
    with open('./plex_pass') as pass_file:
        return pass_file.read()


def pause_then_play():

    username = 'shockn745@gmail.com'
    password = load_password()

    account = MyPlexAccount(username, password)
    debug = account.resources()
    macbook_pro: PlexClient = account.resource('TheMacbookPro').connect()
    duration = int(input('How long to pause for: '))
    macbook_pro.pause()
    sleep(duration)
    macbook_pro.play()


def plex_login():
    # get with auth
    SIGNIN = 'https://plex.tv/users/sign_in.xml'
    PIPEDREAM = 'https://8ae75063b87060749dbab0b02d7dd057.m.pipedream.net'

    username = 'frank'
    password = 'sarah'

    requests.post(PIPEDREAM, auth=(username, password))

    def auth_header():
        encoded_credentials = b64encode(
            f'{username}:{password}'.encode()
        ).decode()
        return f'Basic {encoded_credentials}'

    print(auth_header())
    res = requests.post(PIPEDREAM, headers={'authorization': auth_header()})
    print(res.json())

    username = 'shockn745@gmail.com'
    password = load_password()
    res = requests.post(SIGNIN, headers={
        'authorization': auth_header(),
        'X-Plex-Client-Identifier': 'sandboxPython'
    })
    print(res.text)
    print(auth_header())


plex_login()
