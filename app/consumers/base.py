import logging
from abc import ABCMeta, abstractmethod
from typing import Callable

import pika
from pika.adapters.blocking_connection import BlockingChannel
from pika.channel import Channel
from pika.spec import Basic
from retry import retry

from ..config import QueueConfig


class Consumer(metaclass=ABCMeta):
    def __init__(self, connection: pika.BaseConnection, queue: QueueConfig) -> None:
        self.connection = connection
        self.channel = connection.channel()
        self.channel.queue_declare(queue.name, durable=True)
        for routing_key in queue.bindings:
            self.channel.queue_bind(queue.name, queue.exchange, routing_key)
        self.channel.basic_consume(queue.name, self.__callback)

    @abstractmethod
    def on_message_arrived(
        self,
        channel: Channel,
        method: Basic.Deliver,
        properties: pika.BasicProperties,
        body: bytes,
    ) -> None:
        ...

    def __callback(
        self,
        channel: Channel,
        method: Basic.Deliver,
        properties: pika.BasicProperties,
        body: bytes,
    ):
        logging.info("Message with length of %d arrived" % len(body))
        try:
            self.on_message_arrived(channel, method, properties, body)
        except Exception as exc:
            logging.error(exc)


class StoppedConsuming(Exception):
    pass


class BlockingConsumerRunner:
    def __init__(self, get_consumer: Callable[..., Consumer]) -> None:
        self._get_consumer = get_consumer

    @retry(delay=3)
    def __call__(self) -> None:
        consumer = self._get_consumer()
        if not isinstance(consumer.channel, BlockingChannel):
            raise TypeError("Consumer doesn't support blocking connection")
        logging.info("Runner started")
        try:
            consumer.channel.start_consuming()
            logging.info("Stopping consuming")
            consumer.channel.stop_consuming()
            consumer.connection.close()
        except Exception as exc:
            logging.error(exc)
        finally:
            raise StoppedConsuming("Stopped consuming")
