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


def create_app(testing: bool = False) -> Flask:
    app = Flask(__name__)
    app.testing = testing
    app.container = create_container(testing)
    app.wsgi_app = ProxyFix(app.wsgi_app)
    app.wsgi_app = MiddlewareManager(app)
    app.wsgi_app.add_middleware(auth.JwtAuthMiddleware)
    app.register_error_handler(HTTPException, handle_http_exception)
    api = Api(app)
    api.add_resource(Users, "/users/<int:user_id>")
    return app
