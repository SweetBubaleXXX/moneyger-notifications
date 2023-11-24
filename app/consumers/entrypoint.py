import multiprocessing
import logging

from dependency_injector.wiring import Provide, inject

from ..containers import Container
from .base import BlockingConsumerRunner, Consumer


@inject
def main(consumers: list[Consumer] = Provide[Container.consumers]) -> None:
    with multiprocessing.Pool(processes=len(consumers)) as pool:
        for consumer in consumers:
            runner = BlockingConsumerRunner(consumer)
            pool.apply_async(runner)
        logging.info("Started consuming")
        pool.close()
        pool.join()
