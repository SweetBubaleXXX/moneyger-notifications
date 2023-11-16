from pydantic import BaseModel, BaseSettings, MongoDsn


class DatabaseSettings(BaseModel):
    url: MongoDsn
    user: str | None
    password: str | None


class Settings(BaseSettings):
    database: DatabaseSettings

    class Config:
        env_file = '.env'
        env_nested_delimiter = "_"
