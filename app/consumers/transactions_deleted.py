import json

import pika

from ..config import QueueConfig
from ..services.transactions import TransactionsService
from .base import Consumer, MessageContext


class TransactionsDeletedConsumer(Consumer):
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
            transactions = json.loads(context.body)
        except json.JSONDecodeError:
            self.reject_message(context)
            raise
        self.transactions_service.delete_transactions(transactions)
