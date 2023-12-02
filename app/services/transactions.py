from collections.abc import Collection
from datetime import datetime
from typing import Any, Iterable, Iterator

from bson.decimal128 import Decimal128
from pymongo import ASCENDING, ReplaceOne
from pymongo.database import Database

from ..models import Transaction
from .exceptions import NotFound


class TransactionsService:
    def __init__(self, db: Database):
        self.db = db
        self.collection = self.db.transactions

    @staticmethod
    def serialize_transaction(transaction: Transaction) -> dict[str, Any]:
        serialized_transaction = transaction.dict()
        serialized_transaction["amount"] = Decimal128(transaction.amount)
        return serialized_transaction

    def filter_transactions(
        self,
        account_id: int,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
    ) -> Iterator[Transaction]:
        filters = {"account_id": account_id}
        transaction_time_filters = self._create_time_range_filters(start_time, end_time)
        if transaction_time_filters:
            filters["transaction_time"] = transaction_time_filters
        cursor = self.collection.find(filters).sort("transaction_time", ASCENDING)
        for transaction in cursor:
            yield Transaction(**transaction)

    def add_transactions(self, transactions: Iterable[Transaction]) -> None:
        requests = []
        for transaction in transactions:
            serialized_transaction = self.serialize_transaction(transaction)
            requests.append(
                ReplaceOne(
                    {"transaction_id": transaction.transaction_id},
                    serialized_transaction,
                    upsert=True,
                )
            )
        self.collection.bulk_write(requests)

    def delete_transactions(self, transaction_ids: Collection[int]) -> None:
        delete_result = self.collection.delete_many(
            {"transaction_id": {"$in": list(transaction_ids)}}
        )
        if delete_result.deleted_count != len(transaction_ids):
            raise NotFound("Some transactions not found")

    def _create_time_range_filters(
        self,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
    ) -> dict[str, datetime]:
        time_range_filters = {}
        if start_time:
            time_range_filters["$gte"] = start_time
        if end_time:
            time_range_filters["$lt"] = end_time
        return time_range_filters
