from dependency_injector.wiring import Provide, inject
from flask import request
from flask_restful import Resource
from werkzeug.exceptions import Forbidden

from ..containers import Container
from ..services.users import UsersService


class Users(Resource):
    @inject
    def __init__(
        self,
        users_service: UsersService = Provide[Container.users_service],
    ) -> None:
        super().__init__()
        self.users_service = users_service

    def get(self, user_id: int):
        user = self.users_service.get_user_by_id(user_id)
        if user.account_id != request.user:
            raise Forbidden()
        return user.dict()

    def post(self, user_id: int):
        ...
