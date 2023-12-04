from collections.abc import Collection
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Iterable, Iterator, TypedDict

from bson.decimal128 import Decimal128
from pymongo import ASCENDING, IndexModel, ReplaceOne
from pymongo.database import Database

from ..models import Transaction
from .exceptions import NotFound

_DATE_FORMAT = "%Y-%m-%d"


class TransactionTotalByDate(TypedDict):
    date: date
    total_amount: Decimal


class TransactionsService:
    def __init__(self, db: Database):
        self.db = db
        self.collection = self.db.transactions
        self.collection.create_indexes(
            [
                IndexModel("transaction_id", unique=True),
                IndexModel("account_id"),
            ]
        )

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
        filters = self._create_filters(account_id, start_time, end_time)
        cursor = self.collection.find(filters).sort("transaction_time", ASCENDING)
        for transaction in cursor:
            yield Transaction(**transaction)

    def compute_daily_total(
        self,
        account_id: int,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
    ) -> Iterator[TransactionTotalByDate]:
        filters = self._create_filters(account_id, start_time, end_time)
        pipeline = self._create_daily_total_pipeline(filters)
        cursor = self.collection.aggregate(pipeline)
        for result in cursor:
            yield TransactionTotalByDate(
                date=datetime.strptime(result["date"], _DATE_FORMAT).date(),
                total_amount=result["total_amount"].to_decimal(),
            )

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

    def _create_filters(
        self,
        account_id: int,
        start_time: datetime | None = None,
        end_time: datetime | None = None,
    ) -> dict[str, Any]:
        filters = {"account_id": account_id}
        time_range_filters = {}
        if start_time:
            time_range_filters["$gte"] = start_time
        if end_time:
            time_range_filters["$lt"] = end_time
        if time_range_filters:
            filters["transaction_time"] = time_range_filters
        return filters

    def _create_daily_total_pipeline(self, filters: dict[str, Any]) -> list[dict]:
        return [
            {
                "$match": filters,
            },
            {
                "$group": {
                    "_id": {
                        "$dateToString": {
                            "format": _DATE_FORMAT,
                            "date": "$transaction_time",
                        }
                    },
                    "total_amount": {"$sum": "$amount"},
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "date": "$_id",
                    "total_amount": 1,
                }
            },
        ]
