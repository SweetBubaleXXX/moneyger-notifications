from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

from .config import Settings
from .containers import Container


def create_container(testing: bool = False) -> Container:
    container = Container()
    container.config.from_pydantic(Settings(testing=testing))
    return container


def create_app() -> Flask:
    app = Flask(__name__)
    app.container = create_container()
    app.wsgi_app = ProxyFix(app.wsgi_app)
    return app
