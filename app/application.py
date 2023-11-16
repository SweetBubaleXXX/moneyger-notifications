from flask import Flask

from .containers import Container
from .config import Settings


def create_app() -> Flask:
    container = Container()
    container.config.from_pydantic(Settings())
    app = Flask(__name__)
    app.container = container
    return app
