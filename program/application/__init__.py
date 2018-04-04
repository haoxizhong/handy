from flask import Flask
import os

app = Flask(__name__, static_folder='static_dist', static_url_path='/static')


def initialize(routed=True):
    server_dir = os.path.dirname(os.path.realpath(__file__))
    config_file = os.path.join(server_dir, 'config.py')

    app.config.from_pyfile(config_file)

    if routed:
        from . import route
