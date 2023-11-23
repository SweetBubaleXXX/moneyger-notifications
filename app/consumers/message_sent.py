import pika
from pika.channel import Channel
from pika.spec import Basic
from pydantic import ValidationError

from ..config import QueueConfig
from ..models import Message
from ..services.messages import MessageStorage
from .base import Consumer


class MessageSentConsumer(Consumer):
    def __init__(
        self,
        connection: pika.BaseConnection,
        queue: QueueConfig,
        message_storage: MessageStorage,
    ) -> None:
        super().__init__(connection, queue)
        self.message_storage = message_storage

    def callback(
        self,
        channel: Channel,
        method: Basic.Deliver,
        properties: pika.BasicProperties,
        body: bytes,
    ) -> None:
        try:
            message = Message.parse_raw(body)
        except ValidationError:
            return channel.basic_reject(method.delivery_tag, requeue=False)
        self.message_storage.push(message)
        channel.basic_ack(method.delivery_tag)
