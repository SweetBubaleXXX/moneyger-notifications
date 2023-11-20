import pytest
from pymongo.database import Database

from app.application import container
from app.models import User, UserCredentials
from app.services.users import AlreadyExists, NotFound, UsersService

from .factories import UserFactory


@pytest.fixture
def service():
    return UsersService(container.db)


@pytest.fixture
def user():
    return UserFactory()


@pytest.fixture
def saved_user(db: Database, user: User):
    db.users.insert_one(user.dict())
    return user


def test_get_user_by_id(
    service: UsersService,
    saved_user: User,
):
    found_user = service.get_user_by_id(saved_user.account_id)
    assert found_user.token == saved_user.token


def test_get_user_by_credentials(
    service: UsersService,
    saved_user: User,
):
    invalid_credentials = UserCredentials(
        account_id=0,
        email=saved_user.email,
        token="invalid_token",
    )
    with pytest.raises(NotFound):
        service.get_user_by_credentials(invalid_credentials)


def test_create_user(
    db: Database,
    service: UsersService,
    user: User,
):
    service.create_user(user)
    user_in_db = db.users.find_one(user.dict())
    assert user_in_db


def test_create_user_already_exists(
    db: Database,
    service: UsersService,
    saved_user: User,
):
    db.users.insert_one(saved_user.dict())
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


def test_delete_user_not_found(
    service: UsersService,
    user: User,
):
    with pytest.raises(NotFound):
        service.delete_user(user.account_id)
