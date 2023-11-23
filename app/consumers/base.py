from abc import ABCMeta, abstractmethod
from typing import Iterable

import pika
from pika.channel import Channel
from pika.spec import Basic


class Consumer(metaclass=ABCMeta):
    def __init__(
        self,
        connection: pika.BaseConnection,
        exchange_name: str,
        queue_name: str,
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
