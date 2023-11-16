from app.application import container

from .conftest import TEST_DB_NAME


def test_db_name():
    assert container.db().name == TEST_DB_NAME
