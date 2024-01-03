import pika

from ..config import QueueConfig
from ..models import UserCredentialsResponse
from ..services.exceptions import NotFound
from ..services.users import UsersService
from .base import Consumer, MessageContext


class UserCredentialsRpc(Consumer):
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
        except ValueError:
            self.reject_message(context)
            raise
        try:
            user = self.users_service.get_user_by_id(account_id)
        except NotFound:
            self._send_response(UserCredentialsResponse(success=False), context)
            self.acknowledge_positive(context)
            raise
        response = UserCredentialsResponse(success=True, result=user.credentials)
        self._send_response(response, context)

    def _send_response(
        self,
        response: UserCredentialsResponse,
        context: MessageContext,
    ) -> None:
        context.channel.basic_publish(
            exchange="",
            routing_key=context.properties.reply_to,
            properties=pika.BasicProperties(
                correlation_id=context.properties.correlation_id
            ),
            body=response.json(),
        )
