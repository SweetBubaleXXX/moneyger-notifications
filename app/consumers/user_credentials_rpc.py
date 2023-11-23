from typing import Iterable

import pika
from pika.channel import Channel
from pika.spec import Basic

from ..services import users
from ..models import UserCredentialsResponse
from .base import Consumer


class UserCredentialsRpc(Consumer):
    def __init__(
        self,
        connection: pika.BaseConnection,
        queue_name: str,
        exchange_name: str,
        binding_keys: Iterable[str],
        response_exchange_name: str,
        users_service: users.UsersService,
    ) -> None:
        super().__init__(connection, queue_name, exchange_name, binding_keys)
        self.response_exchange = response_exchange_name
        self.users_service = users_service

    def callback(
        self,
        channel: Channel,
        method: Basic.Deliver,
        properties: pika.BasicProperties,
        body: bytes,
    ) -> None:
        try:
            account_id = int(body)
        except ValueError:
            return channel.basic_reject(method.delivery_tag, requeue=False)
        try:
            user = self.users_service.get_user_by_id(account_id)
        except users.NotFound:
            return self._send_response(
                UserCredentialsResponse(success=False),
                channel,
                method,
                properties,
            )
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
            exchange=self.response_exchange,
            routing_key=properties.reply_to,
            properties=pika.BasicProperties(correlation_id=properties.correlation_id),
            body=response.json(),
        )
        channel.basic_ack(method.delivery_tag)
