from typing import Any, Callable

import jwt
from flask import Request, Response
from flask_http_middleware import BaseHTTPMiddleware
from py_auth_header_parser import parse_auth_header
from pydantic import ValidationError


class AuthenticationFailed(BaseException):
    pass


class NotAuthorized(BaseException):
    pass


class JwtAuthMiddleware(BaseHTTPMiddleware):
    def dispatch(self, request: Request, call_next: Callable[..., Any]) -> Response:
        auth_header = request.headers.get("authorization")
        if not auth_header:
            raise NotAuthorized()
        parsed_header = parse_auth_header(auth_header)
        access_token = parsed_header.get("access_token")
        if not access_token:
            raise AuthenticationFailed()
        try:
            ...
        except (jwt.InvalidTokenError, ValidationError) as exc:
            raise AuthenticationFailed() from exc
        return call_next(request)
