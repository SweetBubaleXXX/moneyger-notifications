import logging

from app.application import create_container
from app.consumers.entrypoint import main

if __name__ == "__main__":
    container = create_container()
    logging.basicConfig(
        format="(%(threadName)s) [%(asctime)s] [%(levelname)s]: %(message)s",
        level=container.config.log_level(),
    )
    main()
