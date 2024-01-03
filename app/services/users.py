from typing import Any, Iterator, Mapping

from pymongo import ReturnDocument
from pymongo.database import Database
from pymongo.errors import DuplicateKeyError

from ..models import User
from .exceptions import AlreadyExists, NotFound


class UsersService:
    def __init__(self, db: Database):
        self.db = db
        self.collection = self.db.users
        self.collection.create_index("account_id", unique=True)

    def get_user_by_id(self, account_id: int) -> User:
        user = self.collection.find_one({"account_id": account_id})
        return self._return_user_or_error(user)

    def filter_users(self, filters: Mapping[str, Any]) -> Iterator[User]:
        cursor = self.collection.find(filters)
        for user in cursor:
            yield User(**user)

    def create_user(self, user: User) -> User:
        try:
            self.collection.insert_one(user.dict())
        except DuplicateKeyError as exc:
            raise AlreadyExists(
                f"Account with id({user.account_id}) already exists"
            ) from exc
        return user

    def update_user(self, user: User) -> User:
        updated_user = self.collection.find_one_and_update(
            user.credentials.dict(),
            {"$set": user.settings.dict()},
            return_document=ReturnDocument.AFTER,
        )
        return self._return_user_or_error(updated_user)

    def delete_user(self, account_id: int) -> None:
        delete_result = self.collection.delete_one({"account_id": account_id})
        if not delete_result.deleted_count:
            raise NotFound(f"Account with id({account_id}) not found")

    def _return_user_or_error(self, user: Mapping | None) -> User:
        if not user:
            raise NotFound("User not found")
        return User(**user)
