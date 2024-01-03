from celery import Celery

from ..containers import Container


def create_celery_app(container: Container) -> Celery:
    app = Celery("celery", include=["app.celery.tasks"])
    app.config_from_object(container.config(), namespace="celery")
    return app
