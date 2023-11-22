from typing import Any, AnyStr, Callable

import jwt
from dependency_injector.wiring import Provide, inject
from flask import Request, Response
from flask_http_middleware import BaseHTTPMiddleware
from py_auth_header_parser import parse_auth_header
from pydantic import ValidationError
from werkzeug.datastructures import WWWAuthenticate
from werkzeug.exceptions import BadRequest, Unauthorized

from ..containers import Container
from ..models import JwtTokenPayload, User
from ..services import users


class JwtAuthMiddleware(BaseHTTPMiddleware):
    www_authenticate = WWWAuthenticate("Bearer", {"realm": "api"})

    @inject
    def __init__(
        self,
        users_service: users.UsersService = Provide[Container.users_service],
    ) -> None:
        super().__init__()
        self.users_service = users_service

    def dispatch(self, request: Request, call_next: Callable[..., Any]) -> Response:
        auth_header = request.headers.get("authorization")
        if not auth_header:
            raise Unauthorized(www_authenticate=self.www_authenticate)
        parsed_header = parse_auth_header(auth_header)
        access_token = parsed_header.get("access_token")
        if not access_token:
            raise Unauthorized(www_authenticate=self.www_authenticate)
        user = self._authenticate_user(access_token)
        request.user = user
        return call_next(request)

    def _authenticate_user(self, token: AnyStr) -> User:
        try:
            token_payload = JwtTokenPayload.parse_obj(
                jwt.decode(token, options={"verify_signature": False})
            )
            user = self.users_service.get_user_by_id(token_payload.account_id)
            jwt.decode(token, user.token)
            return user
        except (jwt.InvalidTokenError, ValidationError, users.NotFound) as exc:
            raise BadRequest("Invalid token") from exc
