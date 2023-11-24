import multiprocessing

from dependency_injector.wiring import inject, Provide

from ..containers import Container
from .base import Consumer, BlockingConsumerRunner


@inject
def main(consumers: list[Consumer] = Provide[Container.consumers]) -> None:
    pool = multiprocessing.Pool(processes=len(consumers))
    for consumer in consumers:
        runner = BlockingConsumerRunner(consumer)
        pool.apply_async(runner)
        try:
            while True:
                continue
        except KeyboardInterrupt:
            pool.terminate()
            pool.join()
