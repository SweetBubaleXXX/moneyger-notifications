from typing import Callable, ParamSpec, TypeVar

from dependency_injector.wiring import Provide, inject
from flask import request
from flask_restful import Resource
from pydantic import ValidationError
from werkzeug.exceptions import BadRequest, Forbidden

from ..containers import Container
from ..models import UserSettings
from ..services.users import UsersService

P = ParamSpec("P")
R = TypeVar("R")


def validate_request_user(func: Callable[P, R]) -> Callable[P, R]:
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        if kwargs.get("user_id") != request.user.account_id:
            raise Forbidden()
        return func(*args, **kwargs)

    return wrapper


class Users(Resource):
    method_decorators = [validate_request_user]

    @inject
    def __init__(
        self,
        users_service: UsersService = Provide[Container.users_service],
    ) -> None:
        super().__init__()
        self.users_service = users_service

    def get(self, user_id: int):
        return request.user.settings.dict()

    def put(self, user_id: int):
        try:
            settings = UserSettings.parse_obj(request.json)
        except ValidationError as exc:
            raise BadRequest(str(exc)) from exc
        updated_user = request.user.copy_with_updated_settings(settings)
        updated_user = self.users_service.update_user(updated_user)
        return settings.dict()
