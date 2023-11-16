from typing import Callable

from pymongo.database import Database

from ..models import User


class UsersService:
    def __init__(self, get_db: Callable[..., Database]):
        self.db = get_db()

    def get_users(self) -> list[User]:
        all_users = self.db.users.find()
        return [User.parse_obj(user) for user in all_users]

    def create_user(self, user: User):
        return self.db.users.insert_one(user.dict())
