from pydantic import BaseSettings, MongoDsn, RedisDsn, root_validator


class Settings(BaseSettings):
    testing: bool = False
    database_url: MongoDsn | None
    database_user: str | None
    database_password: str | None
    cache_url: RedisDsn | None
    message_storage_max_size: int = 100

    @root_validator
    def check_production_required_settings(cls, values):
        production_required_settings = ["database_url", "cache_url"]
        testing = values.get("testing")
        if not testing:
            for field in production_required_settings:
                assert values.get(field) is not None, f"{field} setting is required"
        return values

    class Config:
        env_file = ".env"
