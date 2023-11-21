from http import HTTPStatus

from flask.testing import FlaskClient


def test_unauthorized(client: FlaskClient):
    response = client.get("/users/123")
    assert response.status_code == HTTPStatus.UNAUTHORIZED


def test_bad_token(client: FlaskClient):
    response = client.get("/users/123", headers={"authorization": "Bearer bad_token"})
    assert response.status_code == HTTPStatus.BAD_REQUEST
