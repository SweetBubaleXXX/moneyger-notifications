from http import HTTPStatus

import jwt
import pytest
from flask.testing import FlaskClient

from app.models import User, JwtTokenPayload


@pytest.fixture
def jwt_token(saved_user: User):
    token_payload = JwtTokenPayload(account_id=saved_user.account_id)
    return jwt.encode(token_payload.dict(), saved_user.token)


@pytest.fixture
def auth_headers(jwt_token: str):
    return {"authorization": f"Bearer {jwt_token}"}


def test_unauthorized(client: FlaskClient):
    response = client.get("/users/123")
    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_bad_token(client: FlaskClient):
    response = client.get("/users/123", headers={"authorization": "Bearer bad_token"})
    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_invalid_user_id(client: FlaskClient, auth_headers: dict[str, str]):
    response = client.get("/users/123", headers=auth_headers)
    assert response.status_code == HTTPStatus.FORBIDDEN
