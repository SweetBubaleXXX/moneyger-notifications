from flask import Flask

from .containers import Container


def create_app() -> Flask:
    container = Container()
    app = Flask(__name__)
    app.container = container
    return app
