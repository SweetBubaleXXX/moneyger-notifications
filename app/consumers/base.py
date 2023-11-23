from abc import ABCMeta, abstractmethod

import pika
from pika.channel import Channel
from pika.spec import Basic

from ..config import QueueConfig


class Consumer(metaclass=ABCMeta):
    def __init__(self, connection: pika.BaseConnection, queue: QueueConfig) -> None:
        self.connection = connection
        self.channel = connection.channel()
        self.channel.queue_declare(queue.name, durable=True)
        for routing_key in queue.bindings:
            self.channel.queue_bind(queue.name, queue.exchange, routing_key)
        self.channel.basic_consume(queue.name, self.callback)

    @abstractmethod
    def callback(
        self,
        channel: Channel,
        method: Basic.Deliver,
        properties: pika.BasicProperties,
        body: bytes,
    ) -> None:
        ...
