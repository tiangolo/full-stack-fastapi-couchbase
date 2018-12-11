# Import standard library modules


from app.core.celery_app import celery_app
# Import app code
# Absolute imports for Hydrogen (Jupyter Kernel) compatibility
from app.core.config import SENTRY_DSN
# Import installed packages
from raven import Client

client_sentry = Client(SENTRY_DSN)


@celery_app.task(acks_late=True)
def test_celery(word: str):
    return f"test task return {word}"
