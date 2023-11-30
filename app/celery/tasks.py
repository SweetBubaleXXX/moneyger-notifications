from celery import shared_task
from dependency_injector.wiring import Provide, inject

from ..containers import Container
from ..services.email import EmailService
from ..services.messages import MessageStorage


@shared_task(ignore_result=True)
@inject
def notify_recent_messages(
    email_service: EmailService = Provide[Container.email_service],
    message_storage: MessageStorage = Provide[Container.message_storage],
):
    email_service.notify_recent_messages(message_storage)
