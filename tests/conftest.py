import mongomock
import pytest
from dependency_injector import providers

from app.application import container, create_app


@pytest.fixture(scope="function", autouse=True)
def mock_database():
    container.db_client.override(providers.Singleton(mongomock.MongoClient))
    yield
    container.db.reset_override()


@pytest.fixture
def app():
    app = create_app()
    app.testing = True
    yield app
