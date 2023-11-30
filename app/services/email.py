from operator import attrgetter

from redmail import EmailSender

from .messages import MessageStorage
from .users import UsersService


class EmailService:
    def __init__(
        self,
        connection: EmailSender,
        users_service: UsersService,
        message_storage: MessageStorage,
    ) -> None:
        self.connection = connection
        self.users_service = users_service
        message_storage.add_storage_exhausted_listener(self.notify_recent_messages)

    def notify_recent_messages(self, message_storage: MessageStorage) -> None:
        recipients = list(
            map(
                attrgetter("email"),
                self.users_service.filter_users({"subscribed_to_chat": True}),
            )
        )
        recent_messages = message_storage.get_all()
        self.connection.send(
            subject="New messages",
            receivers=recipients,
            html_template="recent_messages.html",
            body_params={
                "messages": recent_messages,
            },
        )
        message_storage.clear()
