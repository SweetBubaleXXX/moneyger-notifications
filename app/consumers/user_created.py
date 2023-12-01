import pika
from pika.channel import Channel
from pika.spec import Basic
from pydantic import ValidationError

from ..config import QueueConfig
from ..models import User
from ..services.exceptions import AlreadyExists
from ..services.users import UsersService
from .base import Consumer


class UserCreatedConsumer(Consumer):
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
            user = User.parse_raw(body)
            self.users_service.create_user(user)
        except (ValidationError, AlreadyExists):
            channel.basic_reject(method.delivery_tag, requeue=False)
            raise
        channel.basic_ack(method.delivery_tag)
