import redis
from dependency_injector import containers, providers
from pymongo import MongoClient

from .services.messages import RedisMessageStorage
from .services.users import UsersService


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        packages=[
            ".services",
            ".middleware",
            ".resources",
        ],
    )

    config = providers.Configuration()
    db_client = providers.Singleton(
        MongoClient,
        config.database_url,
        username=config.database_user,
        password=config.database_password,
    )
    db = providers.Singleton(
        lambda db_client: db_client.get_default_database("default"),
        db_client,
    )
    cache = providers.Singleton(redis.from_url, config.cache_url)
    users_service = providers.Factory(UsersService, db)
    message_storage = providers.Factory(
        RedisMessageStorage,
        cache,
        config.message_storage_max_size,
    )
