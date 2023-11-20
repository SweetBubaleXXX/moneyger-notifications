import pytest

from app.containers import Container
from app.models import Message
from app.services.messages import MessageStorage

from .factories import MessageFactory


@pytest.fixture
def storage(container: Container):
    return container.message_storage()


@pytest.fixture
def message():
    return MessageFactory()


@pytest.fixture
def saved_message(storage: MessageStorage, message: Message):
    storage.push(message)
    return message


def test_push(storage: MessageStorage, message: Message):
    storage.push(message)
    assert len(storage) == 1


def test_get_all(storage: MessageStorage):
    sender = "John Doe"
    message_count = 10
    for _ in range(message_count):
        storage.push(MessageFactory(sender=sender))
    saved_messages = storage.get_all()
    assert len(saved_messages) == message_count
    for message in saved_messages:
        assert message.sender == sender


def test_len_empty(storage: MessageStorage):
    assert len(storage) == 0


def test_contains(storage: MessageStorage, saved_message: Message):
    assert saved_message.id in storage


def test_not_contains(storage: MessageStorage, message: Message):
    assert message.id not in storage
