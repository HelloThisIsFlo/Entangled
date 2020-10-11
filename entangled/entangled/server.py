from flask import Flask, render_template
import sys
import atexit

from entangled.logger import logger
from entangled.entangled import Entangled


ENVS = [
    'prod',
    'e2e_tests',
    'unit_tests'
]


def initialize_app(env):
    def initialize_deps():
        if env == 'prod' or env == 'e2e_tests':
            app.config['ENTANGLED'].connect_to_mqtt()

    if env not in ENVS:
        raise ValueError(f"Invalid env name: '{env}'")

    app = Flask(__name__, template_folder='../templates')
    app.config['ENTANGLED'] = Entangled()

    initialize_deps()

    @app.route('/')
    def main_page():
        return render_template('main_page.html')

    @app.route('/play', methods=['POST'])
    def play():
        app.config['ENTANGLED'].play()
        return 'playing'

    return app
