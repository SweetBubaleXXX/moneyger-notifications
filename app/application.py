from flask import Flask

from .config import Settings
from .containers import Container


def create_container() -> Container:
    container = Container()
    container.config.from_pydantic(Settings())
    return container


def create_app() -> Flask:
    app = Flask(__name__)
    app.container = create_container()
    return app
