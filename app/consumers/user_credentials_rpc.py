import pika
from pika.channel import Channel
from pika.spec import Basic

from ..config import QueueConfig
from ..models import UserCredentialsResponse
from ..services.exceptions import NotFound
from ..services.users import UsersService
from .base import Consumer


class UserCredentialsRpc(Consumer):
    def __init__(
        self,
        connection: pika.BaseConnection,
        queue: QueueConfig,
        users_service: UsersService,
    ) -> None:
        super().__init__(connection, queue)
        self.users_service = users_service

    def process_message(
        self,
        channel: Channel,
        method: Basic.Deliver,
        properties: pika.BasicProperties,
        body: bytes,
    ) -> None:
        try:
            account_id = int(body)
        except ValueError:
            channel.basic_reject(method.delivery_tag, requeue=False)
            raise
        try:
            user = self.users_service.get_user_by_id(account_id)
        except NotFound:
            self._send_response(
                UserCredentialsResponse(success=False),
                channel,
                method,
                properties,
            )
            raise
        response = UserCredentialsResponse(success=True, result=user.credentials)
        self._send_response(response, channel, method, properties)

    def _send_response(
        self,
        response: UserCredentialsResponse,
        channel: Channel,
        method: Basic.Deliver,
        properties: pika.BasicProperties,
    ) -> None:
        channel.basic_publish(
            exchange="",
            routing_key=properties.reply_to,
            properties=pika.BasicProperties(correlation_id=properties.correlation_id),
            body=response.json(),
        )
        channel.basic_ack(method.delivery_tag)
