from collections.abc import Collection
from datetime import date, datetime
from decimal import Decimal
from typing import Any, Iterable, Iterator, NotRequired, TypedDict

from bson.decimal128 import Decimal128
from pymongo import ASCENDING, IndexModel, ReplaceOne
from pymongo.database import Database

from ..models import Transaction, TransactionType
from .exceptions import NotFound

_DATE_FORMAT = "%Y-%m-%d"


class TransactionFilters(TypedDict):
    account_id: NotRequired[int]
    transaction_type: NotRequired[TransactionType]
    start_time: NotRequired[datetime]
    end_time: NotRequired[datetime]


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
                IndexModel("transaction_type"),
                IndexModel("account_id"),
            ]
        )

    @staticmethod
    def serialize_transaction(transaction: Transaction) -> dict[str, Any]:
        serialized_transaction = transaction.dict()
        serialized_transaction["amount"] = Decimal128(transaction.amount)
        return serialized_transaction

    def filter_transactions(self, filters: TransactionFilters) -> Iterator[Transaction]:
        query = self._create_query(filters)
        cursor = self.collection.find(query).sort("transaction_time", ASCENDING)
        for transaction in cursor:
            yield Transaction(**transaction)

    def compute_daily_total(
        self,
        filters: TransactionFilters,
    ) -> Iterator[TransactionTotalByDate]:
        query = self._create_query(filters)
        pipeline = self._create_daily_total_pipeline(query)
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

    def _create_query(self, filters: TransactionFilters) -> dict[str, Any]:
        query_filters = filters.copy()
        start_time = query_filters.pop("start_time", None)
        end_time = query_filters.pop("end_time", None)

        time_range_filters = {}
        if start_time:
            time_range_filters["$gte"] = start_time
        if end_time:
            time_range_filters["$lt"] = end_time

        if time_range_filters:
            query_filters["transaction_time"] = time_range_filters
        return query_filters

    def _create_daily_total_pipeline(self, query: dict[str, Any]) -> list[dict]:
        return [
            {
                "$match": query,
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
