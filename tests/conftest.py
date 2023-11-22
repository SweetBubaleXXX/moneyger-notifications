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


@pytest.fixture(autouse=True)
def mock_database(container: Container):
    container.db_client.override(providers.Singleton(mongomock.MongoClient))
    yield
    container.db_client.reset_override()


@pytest.fixture(autouse=True)
def mock_cache(container: Container):
    container.cache.override(providers.Singleton(fakeredis.FakeRedis))
    yield
    container.cache.reset_override()


@pytest.fixture
def db(container: Container, mock_database):
    return container.db()


@pytest.fixture
def cache(container: Container, mock_cache):
    return container.cache()


@pytest.fixture
def app(container: Container, mock_database, mock_cache):
    app = application.create_app(container)
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
