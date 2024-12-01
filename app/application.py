from .config import Settings
from .containers import Container


def create_container(testing: bool = False) -> Container:
    container = Container()
    container.config.from_pydantic(Settings(testing=testing))
    return container
