import pika
from pydantic import ValidationError

from ..config import QueueConfig
from ..models import Message
from ..services.messages import MessageStorage
from .base import Consumer, MessageContext


class MessageSentConsumer(Consumer):
    def __init__(
        self,
        connection: pika.BaseConnection,
        queue: QueueConfig,
        message_storage: MessageStorage,
    ) -> None:
        super().__init__(connection, queue)
        self.message_storage = message_storage

    def process_message(self, context: MessageContext) -> None:
        try:
            message = Message.parse_raw(context.body)
        except ValidationError:
            self.reject_message(context)
            raise
        self.message_storage.push(message)
