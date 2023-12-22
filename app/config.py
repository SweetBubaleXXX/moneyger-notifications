from typing import Iterable, Literal

from celery.schedules import crontab
from pika.exchange_type import ExchangeType
from pydantic import (
    AmqpDsn,
    AnyUrl,
    BaseModel,
    BaseSettings,
    MongoDsn,
    RedisDsn,
    root_validator,
)


class ExchangeConfig(BaseModel):
    name: str
    exchange_type: ExchangeType = ExchangeType.topic
    durable: bool = True


class QueueConfig(BaseModel):
    exchange: ExchangeConfig
    name: str
    durable: bool = True
    bindings: Iterable[str]


class UserCreatedQueueConfig(QueueConfig):
    name: str = "subscribe_user_to_notifications_queue"
    bindings: Iterable[str] = ["user.event.created"]


class UserDeletedQueueConfig(QueueConfig):
    name: str = "unsubscribe_user_queue"
    bindings: Iterable[str] = ["user.event.deleted"]


class UserCredentialsRpcQueue(QueueConfig):
    name: str = "request_user_credentials_queue"
    bindings: Iterable[str] = ["user.request.credentials"]


class TransactionsAddedQueueConfig(QueueConfig):
    name: str = "transaction_updates_queue"
    bindings: Iterable[str] = ["transaction.event.created", "transaction.event.updated"]


class TransactionsDeletedQueueConfig(QueueConfig):
    name: str = "transaction_removal_queue"
    bindings: Iterable[str] = ["transaction.event.deleted"]


class MessageSentQueueConfig(QueueConfig):
    name: str = "new_messages_queue"
    bindings: Iterable[str] = ["message.event.sent"]


class Settings(BaseSettings):
    testing: bool = False
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = "INFO"

    database_url: MongoDsn | None
    database_user: str | None
    database_password: str | None
    default_database: str = "default_db"

    cache_url: RedisDsn | None

    mail_host: str | None
    mail_port: int | None
    mail_user: str | None
    mail_password: str | None

    celery_broker_url: AnyUrl | None
    celery_result_backend: AnyUrl | None
    celery_beat_schedule: dict[str, dict] = {
        "notify-recent-messages-daily": {
            "task": "app.celery.tasks.notify_recent_messages",
            "schedule": crontab(minute=0, hour=9),
        },
        "send-predictions-weekly": {
            "task": "app.celery.tasks.send_week_predictions",
            "schedule": crontab(minute=0, hour=20, day_of_week="sun"),
        },
        "send-predictions-monthly": {
            "task": "app.celery.tasks.send_month_predictions",
            "schedule": crontab(minute=0, hour=6, day_of_month=1),
        },
    }

    message_storage_max_size: int = 100

    mq_url: AmqpDsn | None
    mq_users_exchange: ExchangeConfig = ExchangeConfig(name="users_exchange")
    mq_transactions_exchange: ExchangeConfig = ExchangeConfig(
        name="transactions_exchange"
    )
    mq_messages_exchange: ExchangeConfig = ExchangeConfig(name="messages_exchange")

    mq_user_created_queue: QueueConfig = UserCreatedQueueConfig(
        exchange=mq_users_exchange
    )
    mq_user_deleted_queue: QueueConfig = UserDeletedQueueConfig(
        exchange=mq_users_exchange
    )
    mq_user_credentials_rpc_queue: QueueConfig = UserCredentialsRpcQueue(
        exchange=mq_users_exchange
    )
    mq_transactions_added_queue: QueueConfig = TransactionsAddedQueueConfig(
        exchange=mq_transactions_exchange
    )
    mq_transactions_deleted_queue: QueueConfig = TransactionsDeletedQueueConfig(
        exchange=mq_transactions_exchange
    )
    mq_message_sent_queue: QueueConfig = MessageSentQueueConfig(
        exchange=mq_messages_exchange
    )

    @root_validator
    def check_production_required_settings(cls, values):
        production_required_settings = [
            "database_url",
            "cache_url",
            "mq_url",
            "mail_host",
            "mail_user",
            "mail_password",
            "celery_broker_url",
            "celery_result_backend",
        ]
        testing = values.get("testing")
        if not testing:
            for field in production_required_settings:
                assert values.get(field) is not None, f"{field} setting is required"
        return values

    class Config:
        env_file = ".env"
        env_nested_delimiter = "_"
