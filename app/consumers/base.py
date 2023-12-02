import logging
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from typing import Callable, Protocol

import pika
from pika.channel import Channel
from pika.spec import Basic

from ..config import QueueConfig


@dataclass
class MessageContext:
    channel: Channel
    method: Basic.Deliver
    properties: pika.BasicProperties
    body: bytes


class Consumer(metaclass=ABCMeta):
    def __init__(self, connection: pika.BaseConnection, queue: QueueConfig) -> None:
        self.connection = connection
        self.channel = connection.channel()
        self.channel.queue_declare(queue.name, durable=True)
        for routing_key in queue.bindings:
            self.channel.queue_bind(queue.name, queue.exchange, routing_key)
        self.channel.basic_consume(queue.name, self.__callback)

    @abstractmethod
    def process_message(self, context: MessageContext) -> None:
        ...

    def acknowledge_positive(self, context: MessageContext) -> None:
        context.channel.basic_ack(context.method.delivery_tag)

    def reject_message(self, context: MessageContext) -> None:
        self._acknowledge_negative(context, requeue=False)

    def skip_message(self, context: MessageContext) -> None:
        self._acknowledge_negative(context, requeue=True)

    def _acknowledge_negative(
        self,
        context: MessageContext,
        requeue: bool,
    ) -> None:
        context.channel.basic_reject(context.method.delivery_tag, requeue)

    def __callback(
        self,
        channel: Channel,
        method: Basic.Deliver,
        properties: pika.BasicProperties,
        body: bytes,
    ):
        logging.info("Message with length of %d arrived", len(body))
        context = MessageContext(channel, method, properties, body)
        try:
            self.process_message(context)
            self.acknowledge_positive(context)
        except Exception as exc:
            logging.error("%s - %s", type(exc).__name__, exc)


class ConsumerExecutor(Protocol):
    def __init__(self, get_consumer: Callable[..., Consumer]) -> None:
        ...

    def __call__(self) -> None:
        ...
