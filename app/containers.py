from dependency_injector import containers, providers
from pymongo import MongoClient


class Container(containers.DeclarativeContainer):
    config = providers.Configuration()
    db_client = providers.Singleton(MongoClient, config.database_url)
    db = providers.Callable(
        lambda db_client: db_client.get_default_database(),
        db_client,
    )
