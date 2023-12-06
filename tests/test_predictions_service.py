from datetime import timedelta

import pytest
from mongomock import Database

from app.containers import Container
from app.models import Transaction
from app.services.exceptions import NotFound
from app.services.predictions import PredictionPeriod, PredictionsService
from app.services.transactions import TransactionsService

from .factories import TransactionFactory


@pytest.fixture
def service(container: Container):
    return container.predictions_service()


@pytest.fixture
def dataset(db: Database, transaction: Transaction):
    transaction_records = []
    for _ in range(40):
        transaction = TransactionFactory(
            account_id=transaction.account_id,
            transaction_time=transaction.transaction_time - timedelta(days=3),
        )
        transaction_records.append(transaction)
    db.transactions.insert_many(
        (
            TransactionsService.serialize_transaction(transaction)
            for transaction in transaction_records
        )
    )
    return transaction_records


def test_predict_week_empty(service: PredictionsService):
    with pytest.raises(NotFound):
        service.predict_week(123)


def test_predict_week(
    service: PredictionsService,
    dataset: list[Transaction],
):
    prediction = service.predict_week(dataset[0].account_id)
    assert prediction > 0


def test_predict_month_empty(service: PredictionsService):
    with pytest.raises(NotFound):
        service.predict_month(123)


def test_predict_month(
    service: PredictionsService,
    dataset: list[Transaction],
):
    prediction = service.predict_month(dataset[0].account_id)
    assert prediction > 0


def test_predict_period(
    service: PredictionsService,
    dataset: list[Transaction],
):
    for period in PredictionPeriod:
        prediction = service.predict_period(dataset[0].account_id, period)
        assert prediction > 0
