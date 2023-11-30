import logging
from abc import ABCMeta, abstractmethod
from typing import Callable, Protocol

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
        self.channel.basic_consume(queue.name, self.__callback)

    def __callback(
        self,
        channel: Channel,
        method: Basic.Deliver,
        properties: pika.BasicProperties,
        body: bytes,
    ):
        logging.info("Message with length of %d arrived", len(body))
        try:
            self.process_message(channel, method, properties, body)
        except Exception as exc:
            logging.error("%s - %s", type(exc).__name__, exc)

    @abstractmethod
    def process_message(
        self,
        channel: Channel,
        method: Basic.Deliver,
        properties: pika.BasicProperties,
        body: bytes,
    ) -> None:
        ...


class ConsumerExecutor(Protocol):
    def __init__(self, get_consumer: Callable[..., Consumer]) -> None:
        ...

    def __call__(self) -> None:
        ...
