from typing import Any, AnyStr, Callable

import jwt
from dependency_injector.wiring import Provide
from flask import Request, Response
from flask_http_middleware import BaseHTTPMiddleware
from py_auth_header_parser import parse_auth_header
from pydantic import ValidationError
from werkzeug.datastructures import WWWAuthenticate
from werkzeug.exceptions import BadRequest, Unauthorized

from ..containers import Container
from ..models import JwtTokenPayload
from ..services import users


class JwtAuthMiddleware(BaseHTTPMiddleware):
    users_service: users.UsersService = Provide[Container.users_service]
    www_authenticate = WWWAuthenticate("Bearer", {"realm": "api"})

    def __init__(self) -> None:
        super().__init__()

    def dispatch(self, request: Request, call_next: Callable[..., Any]) -> Response:
        auth_header = request.headers.get("authorization")
        if not auth_header:
            raise Unauthorized(www_authenticate=self.www_authenticate)
        parsed_header = parse_auth_header(auth_header)
        access_token = parsed_header.get("access_token")
        if not access_token:
            raise Unauthorized(www_authenticate=self.www_authenticate)
        self._verify_token(access_token)
        return call_next(request)

    def _verify_token(self, token: AnyStr) -> None:
        try:
            token_payload = JwtTokenPayload.parse_obj(
                jwt.decode(token, options={"verify_signature": False})
            )
            user = self.users_service.get_user_by_id(token_payload.account_id)
            jwt.decode(token, user.token, ["HS256"])
        except (jwt.InvalidTokenError, ValidationError, users.NotFound) as exc:
            raise BadRequest("Invalid token") from exc
