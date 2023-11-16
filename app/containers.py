from dependency_injector import containers, providers
from pymongo import MongoClient

from .services.users import UsersService


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        packages=[
            ".services",
        ],
    )

    config = providers.Configuration()
    db_client = providers.Singleton(
        MongoClient,
        config.database.url,
        username=config.database.user,
        password=config.database.password,
        authSource="admin",
    )
    db = providers.Callable(
        lambda db_client: db_client.get_default_database(),
        db_client,
    )
    users_service = providers.Factory(UsersService, db)
