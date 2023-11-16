from flask import Flask

from .config import Settings
from .containers import Container

container = Container()
container.config.from_pydantic(Settings())


def create_app() -> Flask:
    app = Flask(__name__)
    app.container = container
    return app
