from logging import log
from flask import Flask, render_template, request, redirect
import atexit
import json

from entangled.logger import logger
from entangled.entangled import Entangled
from entangled.plex import PlexApi, PythonLibPlexApi, MockPlexApi
from entangled.config import config, minutes, seconds


ENVS = [
    'prod',
    'e2e_tests',
    'unit_tests'
]


def initialize_app(env):
    def initialize_deps():
        def tweak_for_e2e_tests():
            # TODO: Find a better way to do this. Maybe by injecting the env in entangled and letting it decide of which
            # TODO: delay to pick but before that, transform the env into an enum.
            start_delay_for_e2e_tests = seconds(300)
            config['entangled']['start_delay'] = start_delay_for_e2e_tests
            config['mqtt']['start_delay'] = start_delay_for_e2e_tests

            # Configure with local mqtt
            config['mqtt']['user'] = 'entangled'
            config['mqtt']['pass'] = 'hello'
            config['mqtt']['domain'] = 'localhost'
            config['mqtt']['port'] = 1883
            config['mqtt']['topic'] = 'entangled'
            config['mqtt']['use-ssl'] = False

        def tweak_for_unit_tests():
            # Disable SSL for unit tests to avoid certificate issues
            config['mqtt']['use-ssl'] = False
            # Use short delay for faster tests
            config['entangled']['start_delay'] = seconds(1)

        if env == 'e2e_tests':
            tweak_for_e2e_tests()
        elif env == 'unit_tests':
            tweak_for_unit_tests()

        if env == 'prod':
            plex_api = PythonLibPlexApi()
        else:
            plex_api = MockPlexApi()

        app.config['PLEX_API'] = plex_api
        app.config['ENTANGLED'] = Entangled(plex_api)

        if env == 'prod' or env == 'e2e_tests':
            app.config['ENTANGLED'].connect_to_mqtt()

    if env not in ENVS:
        raise ValueError(f"Invalid env name: '{env}'")

    app = Flask(__name__, template_folder='../templates')

    initialize_deps()

    @app.route('/')
    def main_page():
        if env == 'e2e_tests':
            return render_template('main_page.html', e2e_tests=True)
        else:
            return render_template('main_page.html')

    @app.route('/play', methods=['POST'])
    def play():
        app.config['ENTANGLED'].send_play_cmd()
        return 'playing'

    @app.route('/pause', methods=['POST'])
    def pause():
        """Pause synchronized playback across all clients"""
        app.config['ENTANGLED'].send_pause_cmd()
        return 'pausing'

    @app.route('/resume', methods=['POST'])
    def resume():
        """Resume synchronized playback across all clients"""
        app.config['ENTANGLED'].send_resume_cmd()
        return 'resuming'

    @app.route('/e2e-mock', methods=['POST'])
    def e2e_mock():
        plex_api: MockPlexApi = app.config['PLEX_API']
        plex_api.mock_current_movie_time = request.form['movie-time']
        if 'reset-mock-calls' in request.form:
            plex_api.mock_calls = []

        return redirect('/')

    @app.route('/e2e-mock-calls', methods=['GET'])
    def e2e_mock_calls():
        plex_api: MockPlexApi = app.config['PLEX_API']
        return json.dumps(plex_api.mock_calls)

    @app.route('/debug', methods=['GET', 'POST'])
    def debug():
        if request.method == 'GET':
            return render_template('debug.html')
        if request.method == 'POST':
            body = request.get_json()
            plex_api: PlexApi = app.config['PLEX_API']

            if 'seekTo' in body:
                seek_to_time = body['seekTo']
                [h, m, s] = list(
                    map(lambda s: int(s), seek_to_time.split(':'))
                )
                plex_api.seek_to(h, m, s)
                return 'ok'

            elif 'play' in body:
                plex_api.play()
                return 'ok'

            elif 'pause' in body:
                plex_api.pause()
                return 'ok'

            elif 'getMovieTime' in body:
                return json.dumps({'currentMovieTime': plex_api.current_movie_time()})

    return app
