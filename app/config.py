from pydantic import BaseModel, BaseSettings, MongoDsn, RedisDsn


class DatabaseSettings(BaseModel):
    url: MongoDsn
    user: str | None
    password: str | None
    default: str = "default_db"


class CacheSettings(BaseModel):
    url: RedisDsn


class Settings(BaseSettings):
    database: DatabaseSettings
    cache: CacheSettings

    class Config:
        env_file = ".env"
        env_nested_delimiter = "_"
