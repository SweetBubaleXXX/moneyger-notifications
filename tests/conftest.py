import pytest
from dependency_injector import providers

from app.application import container, create_app
from app.containers import Container

TEST_DB_NAME = "test_db"


@pytest.fixture(scope="function", autouse=True)
def database():
    container.db.override(
        providers.Callable(
            lambda db_client: db_client[TEST_DB_NAME], Container.db_client
        )
    )
    yield
    db = container.db()
    for collection in db.list_collection_names():
        db[collection].drop()
    container.db.reset_override()


@pytest.fixture()
def app():
    app = create_app()
    app.testing = True
    yield app
