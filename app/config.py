from pydantic import BaseSettings, MongoDsn


class Settings(BaseSettings):
    database_url: MongoDsn

    class Config:
        env_file = '.env'
