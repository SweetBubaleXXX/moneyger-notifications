import logging
from concurrent.futures import ThreadPoolExecutor

from dependency_injector.wiring import Provide, inject

from ..containers import Container
from .base import ConsumerExecutor


@inject
def main(
    consumer_executors: list[ConsumerExecutor] = Provide[Container.consumer_executors],
) -> None:
    thread_pool = ThreadPoolExecutor(max_workers=len(consumer_executors))
    for executor in consumer_executors:
        thread_pool.submit(executor)
    logging.info("Runners created")
    thread_pool.shutdown()
