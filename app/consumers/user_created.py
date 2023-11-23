from typing import Iterable

import pika
from pika.channel import Channel
from pika.spec import Basic
from pydantic import ValidationError

from ..models import User
from ..services import users
from .base import Consumer


class UserCreatedConsumer(Consumer):
    def __init__(
        self,
        connection: pika.BaseConnection,
        exchange_name: str,
        queue_name: str,
        binding_keys: Iterable[str],
        users_service: users.UsersService,
    ) -> None:
        super().__init__(connection, exchange_name, queue_name, binding_keys)
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
