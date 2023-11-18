import pytest

from app.containers import Container
from app.services.messages import MessageStorage


@pytest.fixture
def storage(container: Container):
    return container.message_storage()


def test_len_empty(storage: MessageStorage):
    assert len(storage) == 0
