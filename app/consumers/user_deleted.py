import pika

from ..config import QueueConfig
from ..services.exceptions import NotFound
from ..services.users import UsersService
from .base import Consumer, MessageContext


class UserDeletedConsumer(Consumer):
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
            account_id = int(context.body)
            self.users_service.delete_user(account_id)
        except (ValueError, NotFound):
            self.reject_message(context)
            raise
