import logging
from typing import Callable

from pika.adapters.blocking_connection import BlockingChannel
from retry import retry

from .base import Consumer

_RETRY_DELAY = 3


class StoppedConsuming(Exception):
    pass


class BlockingConsumerExecutor:
    def __init__(self, get_consumer: Callable[..., Consumer]) -> None:
        self._consumer_factory = get_consumer

    @retry(delay=_RETRY_DELAY)
    def __call__(self) -> None:
        consumer = self._create_consumer()
        logging.info("Started consuming")
        try:
            consumer.channel.start_consuming()
        except Exception as exc:
            logging.exception(exc)
        finally:
            consumer.channel.stop_consuming()
            consumer.connection.close()
            raise StoppedConsuming("Stopped consuming")

    def _create_consumer(self) -> Consumer:
        consumer = self._consumer_factory()
        if not isinstance(consumer.channel, BlockingChannel):
            raise TypeError("Consumer doesn't support blocking connection")
        return consumer
