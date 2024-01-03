import pika
from pydantic import ValidationError

from ..config import QueueConfig
from ..models import User
from ..services.exceptions import AlreadyExists
from ..services.users import UsersService
from .base import Consumer, MessageContext


class UserCreatedConsumer(Consumer):
    def __init__(
        self,
        connection: pika.BaseConnection,
        queue: QueueConfig,
        users_service: UsersService,
    ) -> None:
        super().__init__(connection, queue)
        self.users_service = users_service

    def process_message(self, context: MessageContext) -> None:
        try:
            user = User.parse_raw(context.body)
            self.users_service.create_user(user)
        except (ValidationError, AlreadyExists):
            self.reject_message(context)
            raise
