import logging
from concurrent.futures import ThreadPoolExecutor

from dependency_injector.wiring import Provide, inject

from ..containers import Container
from .base import BlockingConsumerRunner, Consumer


@inject
def main(consumers: list[Consumer] = Provide[Container.consumers]) -> None:
    executor = ThreadPoolExecutor(max_workers=len(consumers))
    for consumer in consumers:
        runner = BlockingConsumerRunner(consumer)
        executor.submit(runner)
    logging.info("Started consuming")
    executor.shutdown()
