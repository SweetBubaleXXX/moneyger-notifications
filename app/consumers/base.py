import logging
from abc import ABCMeta, abstractmethod

import pika
from pika.adapters.blocking_connection import BlockingChannel
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


class BlockingConsumerRunner:
    def __init__(self, consumer: Consumer) -> None:
        if not isinstance(consumer.channel, BlockingChannel):
            raise TypeError("Consumer doesn't support blocking connection")
        self.connection = consumer.connection
        self.channel = consumer.channel

    def __call__(self) -> None:
        logging.info("Runner started")
        try:
            self.channel.start_consuming()
        except Exception as exc:
            logging.exception(exc)
        finally:
            self.channel.stop_consuming()
            self.connection.close()
