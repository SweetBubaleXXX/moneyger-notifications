from celery import current_app

from ..containers import Container


def create_celery_app(container: Container):
    app = current_app
    app.config_from_object(container.config(), namespace="celery")
    return app
