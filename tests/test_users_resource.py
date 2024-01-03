from http import HTTPStatus

import jwt
import pytest
from flask.testing import FlaskClient

from app.models import JwtTokenPayload, User, UserSettings


@pytest.fixture
def jwt_token(saved_user: User):
    token_payload = JwtTokenPayload(account_id=saved_user.account_id)
    return jwt.encode(token_payload.dict(), saved_user.token)


@pytest.fixture
def auth_headers(jwt_token: str):
    return {"authorization": f"Bearer {jwt_token}"}


def test_get_user_unauthorized(client: FlaskClient):
    response = client.get("/users/123")
    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_get_user_bad_token(client: FlaskClient):
    response = client.get("/users/123", headers={"authorization": "Bearer bad_token"})
    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_get_user_invalid_user_id(client: FlaskClient, auth_headers: dict):
    response = client.get("/users/123", headers=auth_headers)
    assert response.status_code == HTTPStatus.FORBIDDEN


def test_get_user(client: FlaskClient, saved_user: User, auth_headers: dict):
    response = client.get(f"/users/{saved_user.account_id}", headers=auth_headers)
    assert response.status_code == HTTPStatus.OK
    assert "token" not in response.json
    assert response.json["subscribed_to_chat"] == saved_user.subscribed_to_chat


def test_update_user_invalid_user_id(client: FlaskClient, auth_headers: dict):
    response = client.put("/users/123", headers=auth_headers)
    assert response.status_code == HTTPStatus.FORBIDDEN


def test_update_user_unauthorized(client: FlaskClient):
    response = client.put("/users/123")
    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_update_user_invalid_body(
    client: FlaskClient, saved_user: User, auth_headers: dict
):
    response = client.put(
        f"/users/{saved_user.account_id}",
        headers=auth_headers,
        json={"subscribed_to_chat": "invalid_value"},
    )
    assert response.status_code == HTTPStatus.BAD_REQUEST


def test_update_user(client: FlaskClient, saved_user: User, auth_headers: dict):
    settings = UserSettings(subscribed_to_chat=not saved_user.subscribed_to_chat)
    response = client.put(
        f"/users/{saved_user.account_id}",
        headers=auth_headers,
        json=settings.dict(),
    )
    assert response.status_code == HTTPStatus.OK
    assert response.json["subscribed_to_chat"] == settings.subscribed_to_chat
