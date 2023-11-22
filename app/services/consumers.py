from abc import ABCMeta, abstractmethod
from typing import Iterable

import pika
from pika.channel import Channel
from pika.spec import Basic
from pydantic import ValidationError

from ..models import User
from ..services import users


class ConsumerQueue(metaclass=ABCMeta):
    def __init__(
        self,
        connection: pika.BaseConnection,
        queue_name: str,
        exchange_name: str,
        binding_keys: Iterable[str],
    ) -> None:
        self.connection = connection
        self.channel = connection.channel()
        self.channel.queue_declare(queue_name, durable=True)
        for routing_key in binding_keys:
            self.channel.queue_bind(queue_name, exchange_name, routing_key)
        self.channel.basic_consume(queue_name, self.callback)

    @abstractmethod
    def callback(
        self,
        channel: Channel,
        method: Basic.Deliver,
        properties: pika.BasicProperties,
        body: bytes,
    ) -> None:
        ...


class UserCreatedQueue(ConsumerQueue):
    def __init__(
        self,
        connection: pika.BaseConnection,
        queue_name: str,
        exchange_name: str,
        binding_keys: Iterable[str],
        users_service: users.UsersService,
    ) -> None:
        super().__init__(connection, queue_name, exchange_name, binding_keys)
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
