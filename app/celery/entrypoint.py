from ..application import create_container
from .app import create_celery_app

container = create_container()
app = create_celery_app(container)
