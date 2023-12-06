from datetime import timedelta
from decimal import Decimal
from operator import attrgetter

import pytest
from mongomock import Database

from app.containers import Container
from app.models import Transaction
from app.services.exceptions import NotFound
from app.services.transactions import TransactionsService

from .factories import TransactionFactory


@pytest.fixture
def service(container: Container):
    return container.transactions_service()


def test_filter_transactions_not_found(
    service: TransactionsService,
):
    result = service.filter_transactions(account_id=0)
    assert list(result) == []


def test_filter_transactions_without_time_range(
    service: TransactionsService,
    saved_transaction: Transaction,
):
    result = service.filter_transactions(account_id=saved_transaction.account_id)
    assert next(result).transaction_id == saved_transaction.transaction_id


def test_filter_transactions_time_range(
    db: Database,
    service: TransactionsService,
    saved_transaction: Transaction,
):
    old_transaction = TransactionFactory(
        transaction_time=saved_transaction.transaction_time - timedelta(days=1)
    )
    new_transaction = TransactionFactory(
        transaction_time=saved_transaction.transaction_time + timedelta(days=1)
    )
    for transaction in (old_transaction, new_transaction):
        serialized_transaction = TransactionsService.serialize_transaction(transaction)
        db.transactions.insert_one(serialized_transaction)
    result = list(
        service.filter_transactions(
            account_id=saved_transaction.account_id,
            start_time=saved_transaction.transaction_time - timedelta(hours=1),
            end_time=saved_transaction.transaction_time + timedelta(hours=1),
        )
    )
    assert len(result) == 1
    assert result[0].account_id == saved_transaction.account_id


def test_compute_daily_total(db: Database, service: TransactionsService):
    account_id = 123
    expected_total = Decimal(100)
    transaction_quantity = 10
    for _ in range(transaction_quantity):
        transaction = TransactionFactory(
            account_id=account_id,
            amount=expected_total / transaction_quantity,
        )
        serialized_transaction = TransactionsService.serialize_transaction(transaction)
        db.transactions.insert_one(serialized_transaction)
    result = service.compute_daily_total(account_id)
    today_total = next(result)
    assert today_total["total_amount"] == expected_total


def test_add_transactions(
    db: Database,
    service: TransactionsService,
    transaction: Transaction,
):
    service.add_transactions([transaction])
    transaction_in_db = db.transactions.find_one(
        {"transaction_id": transaction.transaction_id}
    )
    assert transaction_in_db


@pytest.mark.parametrize("saved_transactions_bulk", [5], indirect=True)
def test_add_transactions_bulk(
    db: Database,
    service: TransactionsService,
    saved_transactions_bulk: list[Transaction],
):
    service.add_transactions(saved_transactions_bulk)
    documents_in_db = db.transactions.count_documents({})
    assert documents_in_db == len(saved_transactions_bulk)


def test_add_transactions_replace(
    db: Database,
    service: TransactionsService,
    saved_transaction: Transaction,
):
    updated_transaction = saved_transaction.copy()
    updated_transaction.amount = saved_transaction.amount + Decimal("1.23")
    service.add_transactions([updated_transaction])
    transaction_in_db = db.transactions.find_one(
        {"transaction_id": saved_transaction.transaction_id}
    )
    assert str(transaction_in_db["amount"]) != str(saved_transaction.amount)


def test_delete_transactions(
    db: Database,
    service: TransactionsService,
    saved_transaction: Transaction,
):
    service.delete_transactions([saved_transaction.transaction_id])
    documents_in_db = db.transactions.count_documents(
        {"transaction_id": saved_transaction.transaction_id}
    )
    assert documents_in_db == 0


@pytest.mark.parametrize("saved_transactions_bulk", [5], indirect=True)
def test_delete_transactions_bulk(
    db: Database,
    service: TransactionsService,
    saved_transactions_bulk: list[Transaction],
):
    transaction_ids = map(attrgetter("transaction_id"), saved_transactions_bulk)
    service.delete_transactions(list(transaction_ids))
    documents_in_db = db.transactions.count_documents({})
    assert documents_in_db == 0


def test_delete_transactions_not_found(service: TransactionsService):
    with pytest.raises(NotFound):
        service.delete_transactions([123])


def test_delete_transactions_bulk_not_found(
    service: TransactionsService,
    saved_transaction: Transaction,
):
    with pytest.raises(NotFound):
        service.delete_transactions([saved_transaction.transaction_id, 123])
