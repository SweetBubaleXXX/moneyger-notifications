import logging
from smtplib import SMTPException
from typing import Collection, Iterable

from redmail import EmailSender

from ..models import Message, User
from .messages import MessageStorage
from .predictions import PredictionPeriod, PredictionsService
from .users import UsersService


class EmailService:
    def __init__(
        self,
        connection: EmailSender,
        users_service: UsersService,
        message_storage: MessageStorage,
        predictions_service: PredictionsService,
    ) -> None:
        self.connection = connection
        self.users_service = users_service
        self.predictions_service = predictions_service
        message_storage.add_storage_exhausted_listener(self.notify_recent_messages)

    def notify_recent_messages(self, message_storage: MessageStorage) -> None:
        subscribed_users = self.users_service.filter_users({"subscribed_to_chat": True})
        recent_messages = message_storage.get_all()
        if not recent_messages:
            return
        with self.connection:
            self._send_recent_messages_notifications(subscribed_users, recent_messages)
        message_storage.clear()

    def send_predictions(self, period: PredictionPeriod) -> None:
        subscribed_users = self.users_service.filter_users(
            {"subscribed_to_predictions": True}
        )
        with self.connection:
            for recipient in subscribed_users:
                try:
                    self._make_and_send_prediction(recipient, period)
                except Exception:
                    logging.exception(
                        "Sending prediction for account %d failed",
                        recipient.account_id,
                    )

    def _send_recent_messages_notifications(
        self,
        recipients: Iterable[User],
        messages: Collection[Message],
    ) -> None:
        for user in recipients:
            try:
                self.connection.send(
                    subject="New messages",
                    receivers=[user.email],
                    html_template="recent_messages.html",
                    body_params={
                        "messages": messages,
                    },
                )
            except SMTPException:
                logging.exception(
                    "Failed to send an email to the account %d",
                    user.account_id,
                )

    def _make_and_send_prediction(self, user: User, period: PredictionPeriod) -> None:
        prediction = self.predictions_service.predict_period(user.account_id, period)
        self.connection.send(
            subject=f"Prediction for a {period.lower()}",
            receivers=[user.email],
            html_template="prediction.html",
            body_params={
                "period": period.lower(),
                "amount": str(prediction),
                "currency_symbol": "$",
            },
        )
