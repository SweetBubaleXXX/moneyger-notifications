import pytest
from redmail import EmailSender

from app.containers import Container
from app.services.messages import MessageStorage

from .factories import MessageFactory


@pytest.fixture(autouse=True)
def email_service(container: Container):
    return container.email_service()


@pytest.fixture
def email_connection(container: Container):
    return container.email_connection()


def test_notify_recent_messages(email_connection: EmailSender, storage: MessageStorage):
    for _ in range(storage.storage_size_limit):
        message = MessageFactory()
        storage.push(message)
    email_connection.send.assert_called_once()
    assert len(storage) == 0