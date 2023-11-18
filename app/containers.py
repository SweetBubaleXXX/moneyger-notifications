import redis
from dependency_injector import containers, providers
from pymongo import MongoClient

from .services.users import UsersService
from .services.messages import RedisMessageStorage


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
    )
    db = providers.Singleton(
        lambda db_client, default_db: db_client.get_default_database(default_db),
        db_client,
        config.database.default,
    )
    cache = providers.Singleton(redis.from_url, config.cache.url)
    users_service = providers.Factory(UsersService, db)
    message_storage = providers.Factory(
        RedisMessageStorage,
        cache,
        config.message_storage_max_size,
    )
