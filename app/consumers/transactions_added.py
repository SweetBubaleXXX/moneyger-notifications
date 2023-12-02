import pika
from pydantic import ValidationError, parse_raw_as

from ..config import QueueConfig
from ..models import Transaction
from ..services.transactions import TransactionsService
from .base import Consumer, MessageContext


class TransactionsAddedConsumer(Consumer):
    def __init__(
        self,
        connection: pika.BaseConnection,
        queue: QueueConfig,
        transactions_service: TransactionsService,
    ) -> None:
        super().__init__(connection, queue)
        self.transactions_service = transactions_service

    def process_message(self, context: MessageContext) -> None:
        try:
            transactions = parse_raw_as(list[Transaction], context.body)
        except ValidationError:
            self.reject_message(context)
            raise
        self.transactions_service.add_transactions(transactions)
