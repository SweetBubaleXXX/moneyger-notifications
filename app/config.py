from pydantic import AmqpDsn, BaseSettings, MongoDsn, RedisDsn, root_validator


class Settings(BaseSettings):
    testing: bool = False

    database_url: MongoDsn | None
    database_user: str | None
    database_password: str | None
    default_database: str = "default_db"

    cache_url: RedisDsn | None

    mq_url: AmqpDsn | None
    mq_user_created_queue: str = "subscribe_user_to_notifications_queue"
    mq_users_exchange: str = "users_exchange"
    mq_user_created_queue_bindings: list[str] = ["user.event.created"]

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
