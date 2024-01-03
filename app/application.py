from flask import Flask
from flask_http_middleware import MiddlewareManager
from flask_restful import Api
from werkzeug.exceptions import HTTPException
from werkzeug.middleware.proxy_fix import ProxyFix

from .config import Settings
from .containers import Container
from .error_handlers import handle_http_exception
from .middleware import auth
from .resources.users import Users


def create_container(testing: bool = False) -> Container:
    container = Container()
    container.config.from_pydantic(Settings(testing=testing))
    return container


def create_app(container: Container | None = None) -> Flask:
    app = Flask(__name__)
    if not container:
        container = create_container()
    app.testing = container.config.testing()
    app.logger.setLevel(container.config.log_level())
    app.container = container
    app.wsgi_app = ProxyFix(
        app.wsgi_app,
        x_for=container.config.xff_trusted_proxy_depth,
        x_proto=container.config.xff_trusted_proxy_depth,
        x_host=container.config.xff_trusted_proxy_depth,
        x_port=container.config.xff_trusted_proxy_depth,
    )
    app.wsgi_app = MiddlewareManager(app)
    app.wsgi_app.add_middleware(auth.JwtAuthMiddleware)
    app.register_error_handler(HTTPException, handle_http_exception)
    api = Api(app)
    api.add_resource(Users, "/users/<int:user_id>")
    return app
