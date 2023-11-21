import fakeredis
import mongomock
import pytest
from dependency_injector import providers
from pymongo.database import Database

from app import application
from app.containers import Container
from app.models import User

from .factories import UserFactory


@pytest.fixture()
def container():
    return application.create_container(testing=True)


@pytest.fixture(scope="function", autouse=True)
def mock_database(container: Container):
    container.db_client.override(providers.Singleton(mongomock.MongoClient))
    yield
    container.db.reset_override()


@pytest.fixture(scope="function", autouse=True)
def mock_cache(container: Container):
    container.cache.override(providers.Singleton(fakeredis.FakeRedis))
    yield
    container.cache.reset_override()


@pytest.fixture
def db(container: Container):
    return container.db()


@pytest.fixture
def cache(container: Container):
    return container.cache()


@pytest.fixture
def app():
    app = application.create_app(testing=True)
    return app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture
def user():
    return UserFactory()


@pytest.fixture
def saved_user(db: Database, user: User):
    db.users.insert_one(user.dict())
    return user
