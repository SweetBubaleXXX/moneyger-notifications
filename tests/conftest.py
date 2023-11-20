import fakeredis
import mongomock
import pytest
from dependency_injector import providers

from app import application
from app.containers import Container


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
    app = application.create_app()
    app.testing = True
    return app
