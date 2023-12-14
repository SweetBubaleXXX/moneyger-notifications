import jinja2
import pika
import redis
from dependency_injector import containers, providers
from pymongo import MongoClient
from redmail import EmailSender

from .config import QueueConfig
from .consumers.base import ConsumerExecutor
from .consumers.executors import BlockingConsumerExecutor
from .consumers.message_sent import MessageSentConsumer
from .consumers.transactions_added import TransactionsAddedConsumer
from .consumers.transactions_deleted import TransactionsDeletedConsumer
from .consumers.user_created import UserCreatedConsumer
from .consumers.user_credentials_rpc import UserCredentialsRpc
from .consumers.user_deleted import UserDeletedConsumer
from .services.email import EmailService
from .services.messages import RedisMessageStorage
from .services.predictions import PredictionsService
from .services.transactions import TransactionsService
from .services.users import UsersService


class Container(containers.DeclarativeContainer):
    wiring_config = containers.WiringConfiguration(
        packages=[
            ".celery",
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
    transactions_service = providers.Factory(TransactionsService, db)
    predictions_service = providers.Factory(PredictionsService, transactions_service)

    message_storage = providers.Singleton(
        RedisMessageStorage,
        cache,
        config.message_storage_max_size,
    )

    jinja_environment = jinja2.Environment(
        loader=jinja2.FileSystemLoader("app/templates")
    )
    email_connection = providers.Factory(
        EmailSender,
        config.mail_host,
        config.mail_port,
        config.mail_user,
        config.mail_password,
    )
    email_connection.add_attributes(
        templates_html=jinja_environment,
        templates_text=jinja_environment,
    )
    email_service = providers.Singleton(
        EmailService,
        email_connection,
        users_service,
        message_storage,
        predictions_service,
    )

    mq_params = providers.Singleton(pika.URLParameters, config.mq_url)
    mq_connection = providers.Factory(pika.BlockingConnection, mq_params)
    queue_config = providers.Object(lambda config: QueueConfig(**config))
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
    transactions_added_consumer = providers.Factory(
        TransactionsAddedConsumer,
        mq_connection,
        queue_config.provided.call(config.mq_transactions_added_queue),
        transactions_service,
    )
    transactions_deleted_consumer = providers.Factory(
        TransactionsDeletedConsumer,
        mq_connection,
        queue_config.provided.call(config.mq_transactions_deleted_queue),
        transactions_service,
    )
    message_sent_consumer = providers.Factory(
        MessageSentConsumer,
        mq_connection,
        queue_config.provided.call(config.mq_message_sent_queue),
        message_storage,
    )
    consumer_executors: list[ConsumerExecutor] = providers.List(
        providers.Factory(BlockingConsumerExecutor, user_created_consumer.provider),
        providers.Factory(BlockingConsumerExecutor, user_deleted_consumer.provider),
        providers.Factory(BlockingConsumerExecutor, user_credentials_rpc.provider),
        providers.Factory(
            BlockingConsumerExecutor,
            transactions_added_consumer.provider,
        ),
        providers.Factory(
            BlockingConsumerExecutor,
            transactions_deleted_consumer.provider,
        ),
        providers.Factory(BlockingConsumerExecutor, message_sent_consumer.provider),
    )
