import pika
import redis
from dependency_injector import containers, providers
from dependency_injector.providers import Factory
from pymongo import MongoClient

from .config import QueueConfig
from .consumers.message_sent import MessageSentConsumer
from .consumers.user_created import UserCreatedConsumer
from .consumers.user_credentials_rpc import UserCredentialsRpc
from .consumers.user_deleted import UserDeletedConsumer
from .consumers.base import Consumer
from .services.messages import RedisMessageStorage
from .services.users import UsersService


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        packages=[
            ".consumers",
            ".middleware",
            ".resources",
            ".services",
        ],
    )
    __self__ = providers.Self()

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
    mq_params = providers.Singleton(pika.URLParameters, config.mq_url)
    mq_connection = providers.Factory(pika.BlockingConnection, mq_params)
    queue_config = providers.Object(lambda config: QueueConfig.construct(**config))
    user_created_consumer = providers.Factory(
        UserCreatedConsumer,
        mq_connection,
        queue_config.provided.call(config.mq_user_created_queue),
        users_service,
    )
    user_deleted_consumer = providers.Factory(
        UserDeletedConsumer,
        mq_connection,
        queue_config.provided.call(config.mq_user_deleted_queue),
        users_service,
    )
    user_credentials_rpc = providers.Factory(
        UserCredentialsRpc,
        mq_connection,
        queue_config.provided.call(config.mq_user_credentials_rpc_queue),
        users_service,
    )
    message_sent_consumer = providers.Factory(
        MessageSentConsumer,
        mq_connection,
        queue_config.provided.call(config.mq_message_sent_queue),
        message_storage,
    )
    consumers: list[Factory[Consumer]] = providers.List(
        user_created_consumer.provider,
        user_deleted_consumer.provider,
        user_credentials_rpc.provider,
        message_sent_consumer.provider,
    )
