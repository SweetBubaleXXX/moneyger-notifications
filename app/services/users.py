from typing import Any, Iterator, Mapping

from pymongo import ReturnDocument
from pymongo.database import Database

from ..models import User, UserCredentials, UserSettings


class AlreadyExists(BaseException):
    pass


class NotFound(BaseException):
    pass


class UsersService:
    def __init__(self, db: Database):
        self.db = db
        self.collection = self.db.users

    def get_user_by_email(self, email: str) -> User:
        user = self.collection.find_one({"email": email})
        return self._return_user_or_error(user)

    def get_user_by_credentials(self, credentials: UserCredentials) -> User:
        user = self.collection.find_one(credentials.dict())
        return self._return_user_or_error(user)

    def filter_users(self, filters: Mapping[str, Any]) -> Iterator[User]:
        cursor = self.collection.find(filters)
        for user in cursor:
            yield User(**user)

    def create_user(self, user: User) -> User:
        existing_user = self.collection.find_one({"email": user.email})
        if existing_user:
            raise AlreadyExists()
        self.collection.insert_one(user.dict())
        return user

    def update_user(self, user: User) -> User:
        user_info = user.dict()
        user_credentials = UserCredentials(**user_info)
        user_settings = UserSettings(**user_info)
        updated_user = self.collection.find_one_and_update(
            user_credentials.dict(),
            {"$set": user_settings.dict()},
            return_document=ReturnDocument.AFTER,
        )
        return self._return_user_or_error(updated_user)

    def delete_user(self, email: str) -> None:
        delete_result = self.collection.delete_one({"email": email})
        if not delete_result.deleted_count:
            raise NotFound()

    def _return_user_or_error(self, user: Mapping | None) -> User:
        if not user:
            raise NotFound()
        return User(**user)
