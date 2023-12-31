import pytest
from mongomock import Database

from app.containers import Container
from app.models import User
from app.services.exceptions import AlreadyExists, NotFound
from app.services.users import UsersService

from .factories import UserFactory


@pytest.fixture
def service(container: Container):
    return container.users_service()


def test_get_user_by_id(
    service: UsersService,
    saved_user: User,
):
    found_user = service.get_user_by_id(saved_user.account_id)
    assert found_user.token == saved_user.token


def test_filter_users_not_found(
    service: UsersService,
    user: User,
):
    result = service.filter_users({"email": user.email})
    assert list(result) == []


def test_filter_users(
    db: Database,
    service: UsersService,
):
    user_count = 10
    for i in range(user_count):
        user = UserFactory(subscribed_to_chat=i % 2)
        db.users.insert_one(user.dict())
    result = list(service.filter_users({"subscribed_to_chat": True}))
    assert len(result) == user_count / 2
    for user in result:
        assert user.subscribed_to_chat


def test_create_user(
    db: Database,
    service: UsersService,
    user: User,
):
    service.create_user(user)
    user_in_db = db.users.find_one(user.dict())
    assert user_in_db


def test_create_user_already_exists(service: UsersService, saved_user: User):
    with pytest.raises(AlreadyExists):
        service.create_user(saved_user)


def test_update_user(
    service: UsersService,
    saved_user: User,
):
    new_user_info = {
        **saved_user.dict(),
        "subscribed_to_chat": not saved_user.subscribed_to_chat,
    }
    updated_user = service.update_user(User(**new_user_info))
    assert updated_user.subscribed_to_chat == new_user_info["subscribed_to_chat"]


def test_update_user_not_found(
    service: UsersService,
    user: User,
):
    with pytest.raises(NotFound):
        service.update_user(user)


def test_delete_user(
    db: Database,
    service: UsersService,
    saved_user: User,
):
    service.delete_user(saved_user.account_id)
    documents_in_db = db.users.count_documents({"account_id": saved_user.account_id})
    assert documents_in_db == 0


def test_delete_user_not_found(service: UsersService):
    with pytest.raises(NotFound):
        service.delete_user(123)
