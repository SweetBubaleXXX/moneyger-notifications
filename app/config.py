from typing import Iterable

from pydantic import (
    AmqpDsn,
    BaseModel,
    BaseSettings,
    MongoDsn,
    RedisDsn,
    root_validator,
)


class QueueConfig(BaseModel):
    exchange: str
    name: str
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


class MessageSentQueueConfig(QueueConfig):
    name: str = "new_messages_queue"
    bindings: Iterable[str] = ["message.event.sent"]


class Settings(BaseSettings):
    testing: bool = False

    database_url: MongoDsn | None
    database_user: str | None
    database_password: str | None
    default_database: str = "default_db"

    cache_url: RedisDsn | None

    mq_url: AmqpDsn | None
    mq_users_exchange: str = "users_exchange"
    mq_messages_exchange: str = "messages_exchange"
    mq_user_created_queue: QueueConfig = UserCreatedQueueConfig(
        exchange=mq_users_exchange
    )
    mq_user_deleted_queue: QueueConfig = UserDeletedQueueConfig(
        exchange=mq_users_exchange
    )
    mq_user_credentials_rpc_queue: QueueConfig = UserCredentialsRpcQueue(
        exchange=mq_users_exchange
    )
    mq_message_sent_queue: QueueConfig = MessageSentQueueConfig(
        exchange=mq_messages_exchange
    )

    message_storage_max_size: int = 100

    @root_validator
    def check_production_required_settings(cls, values):
        production_required_settings = ["database_url", "cache_url", "mq_url"]
        testing = values.get("testing")
        if not testing:
            for field in production_required_settings:
                assert values.get(field) is not None, f"{field} setting is required"
        return values

    class Config:
        env_file = ".env"
        env_nested_delimiter = "_"
