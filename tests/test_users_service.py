import pytest

from app.application import container
from app.services.users import UsersService

from .factories import UserFactory


@pytest.fixture(scope="module")
def service():
    return UsersService(container.db)


def test_get_users(service: UsersService):
    users = service.get_users()
    assert len(users) == 0


def test_create_user(service: UsersService):
    user = UserFactory()
    service.create_user(user)
