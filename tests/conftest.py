from unittest.mock import MagicMock

import fakeredis
import mongomock
import pytest
from dependency_injector import providers
from mongomock import Database
from pytest_mock import MockerFixture
from redmail import EmailSender

from app import application
from app.containers import Container
from app.models import Message, Transaction, User
from app.services.messages import MessageStorage
from app.services.transactions import TransactionsService

from . import factories


@pytest.fixture()
def container():
    return application.create_container(testing=True)


@pytest.fixture(autouse=True)
def mock_database(mocker: MockerFixture, container: Container):
    mocker.patch("mongomock.mongo_client.MongoClient.start_session", autospec=True)
    container.db_client.override(providers.Singleton(mongomock.MongoClient))
    yield
    container.db_client.reset_override()


@pytest.fixture(autouse=True)
def mock_cache(container: Container):
    container.cache.override(providers.Singleton(fakeredis.FakeRedis))
    yield
    container.cache.reset_override()


@pytest.fixture(autouse=True)
def mock_email_connection(container: Container):
    email_service_mock = MagicMock(spec=EmailSender)
    container.email_connection.override(email_service_mock)
    yield
    container.email_connection.reset_override()


@pytest.fixture
def db(container: Container, mock_database):
    return container.db()


@pytest.fixture
def cache(container: Container, mock_cache):
    return container.cache()


@pytest.fixture
def storage(container: Container):
    return container.message_storage()


@pytest.fixture
def app(container: Container, mock_database, mock_cache):
    app = application.create_app(container)
    return app


@pytest.fixture()
def client(app):
    return app.test_client()


@pytest.fixture
def user():
    return factories.UserFactory()


@pytest.fixture
def saved_user(db: Database, user: User):
    db.users.insert_one(user.dict())
    return user


@pytest.fixture
def transaction():
    return factories.TransactionFactory()


@pytest.fixture
def saved_transaction(db: Database, transaction: Transaction):
    serialized_transaction = TransactionsService.serialize_transaction(transaction)
    db.transactions.insert_one(serialized_transaction)
    return transaction


@pytest.fixture
def message():
    return factories.MessageFactory()


@pytest.fixture
def saved_message(storage: MessageStorage, message: Message):
    storage.push(message)
    return message
