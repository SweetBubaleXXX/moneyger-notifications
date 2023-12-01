import pika
from pika.channel import Channel
from pika.spec import Basic

from ..config import QueueConfig
from ..services.exceptions import NotFound
from ..services.users import UsersService
from .base import Consumer


class UserDeletedConsumer(Consumer):
    def __init__(
        self,
        connection: pika.BaseConnection,
        queue: QueueConfig,
        users_service: UsersService,
    ) -> None:
        super().__init__(connection, queue)
        self.users_service = users_service

    def process_message(
        self,
        channel: Channel,
        method: Basic.Deliver,
        properties: pika.BasicProperties,
        body: bytes,
    ) -> None:
        try:
            account_id = int(body)
            self.users_service.delete_user(account_id)
        except (ValueError, NotFound):
            channel.basic_reject(method.delivery_tag, requeue=False)
            raise
        channel.basic_ack(method.delivery_tag)
