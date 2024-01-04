from datetime import timedelta

import pytest
from mongomock import Database
from redmail import EmailSender

from app.containers import Container
from app.models import User
from app.services.email import EmailService
from app.services.messages import MessageStorage
from app.services.predictions import PredictionPeriod
from app.services.transactions import TransactionsService

from .factories import MessageFactory, TransactionFactory, UserFactory


def _create_transactions(db: Database, account_id: int):
    transactions = [TransactionFactory(account_id=account_id)]
    for _ in range(20):
        transaction = TransactionFactory(
            account_id=account_id,
            transaction_time=transactions[-1].transaction_time - timedelta(days=5),
        )
        transactions.append(transaction)
    db.transactions.insert_many(
        (
            TransactionsService.serialize_transaction(transaction)
            for transaction in transactions
        )
    )


@pytest.fixture
def subscribed_users(db: Database):
    recipients = []
    for _ in range(5):
        user = UserFactory(
            subscribed_to_chat=True,
            subscribed_to_predictions=True,
        )
        _create_transactions(db, user.account_id)
        db.users.insert_one(user.dict())
        recipients.append(user)
    return recipients


@pytest.fixture(autouse=True)
def email_service(container: Container):
    return container.email_service()


@pytest.fixture
def email_connection(container: Container):
    return container.email_connection()


def test_notify_recent_messages(
    email_connection: EmailSender,
    storage: MessageStorage,
    subscribed_users: list[User],
):
    for _ in range(storage.storage_size_limit):
        message = MessageFactory()
        storage.push(message)
    assert email_connection.send.call_count == len(subscribed_users)
    assert len(storage) == 0


def test_notify_no_recent_messages(
    email_connection: EmailSender,
    email_service: EmailService,
    storage: MessageStorage,
):
    email_service.notify_recent_messages(storage)
    email_connection.send.assert_not_called()


def test_send_predictions_empty(
    email_connection: EmailSender,
    email_service: EmailService,
):
    email_service.send_predictions(PredictionPeriod.MONTH)
    email_connection.send.assert_not_called()


def test_send_predictions(
    email_connection: EmailSender,
    email_service: EmailService,
    subscribed_users: list[User],
):
    email_service.send_predictions(PredictionPeriod.WEEK)
    assert email_connection.send.call_count == len(subscribed_users)
