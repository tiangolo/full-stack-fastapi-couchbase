from raven import Client

from app.core.celery_app import celery_app
from app.core.config import SENTRY_DSN

client_sentry = Client(SENTRY_DSN)


@celery_app.task(acks_late=True)
def test_celery(word: str):
    return f"test task return {word}"
