import pika
from pika.channel import Channel
from pika.spec import Basic
from pydantic import ValidationError

from ..config import QueueConfig
from ..models import User
from ..services import users
from .base import Consumer


class UserCreatedConsumer(Consumer):
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
            user = User.parse_raw(body)
        except ValidationError:
            return channel.basic_reject(method.delivery_tag, requeue=False)
        self.users_service.create_user(user)
        channel.basic_ack(method.delivery_tag)
