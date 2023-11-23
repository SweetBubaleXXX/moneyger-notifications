import pika
from pika.channel import Channel
from pika.spec import Basic

from ..config import QueueConfig
from ..services import users
from .base import Consumer


class UserDeletedConsumer(Consumer):
    def __init__(
        self,
        connection: pika.BaseConnection,
        queue: QueueConfig,
        users_service: users.UsersService,
    ) -> None:
        super().__init__(connection, queue)
        self.users_service = users_service

    def callback(
        self,
        channel: Channel,
        method: Basic.Deliver,
        properties: pika.BasicProperties,
        body: bytes,
    ) -> None:
        try:
            account_id = int(body)
        except ValueError:
            return channel.basic_reject(method.delivery_tag, requeue=False)
        try:
            self.users_service.delete_user(account_id)
        except users.NotFound:
            pass
        channel.basic_ack(method.delivery_tag)
