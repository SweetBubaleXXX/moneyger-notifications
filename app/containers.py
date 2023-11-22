import pika
import redis
from dependency_injector import containers, providers
from pymongo import MongoClient

from .consumers.user_created import UserCreatedConsumer
from .consumers.user_credentials_rpc import UserCredentialsRpc
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
        lambda db_client, default_db: db_client.get_default_database(default_db),
        db_client,
        config.default_database,
    )
    cache = providers.Singleton(redis.from_url, config.cache_url)
    users_service = providers.Factory(UsersService, db)
    message_storage = providers.Factory(
        RedisMessageStorage,
        cache,
        config.message_storage_max_size,
    )
    mq_params = providers.Singleton(pika.ConnectionParameters, config.mq_url)
    mq_connection = providers.Singleton(pika.BlockingConnection, mq_params)
    user_created_consumer = providers.Factory(
        UserCreatedConsumer,
        mq_connection,
        config.mq_user_created_queue,
        config.mq_users_exchange,
        config.mq_user_created_queue_bindings,
        users_service,
    )
    user_credentials_rpc = providers.Factory(
        UserCredentialsRpc,
        mq_connection,
        config.mq_user_credentials_rpc_queue,
        config.mq_users_exchange,
        config.mq_user_credentials_rpc_queue_bindings,
        config.mq_rpc_response_exchange,
        users_service,
    )
