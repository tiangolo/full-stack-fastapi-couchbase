import logging

from tenacity import retry, stop_after_attempt, wait_fixed, before_log, after_log

from app.tests.api.api_v1.test_token import test_get_access_token

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

max_tries = 60 * 5  # 5 minutes
wait_seconds = 1


@retry(
    stop=stop_after_attempt(max_tries),
    wait=wait_fixed(wait_seconds),
    before=before_log(logger, logging.INFO),
    after=after_log(logger, logging.WARN),
)
def init():
    # Check Couchbase is awake
    from app.db.database import get_default_bucket  # noqa
    bucket = get_default_bucket()
    logger.info(f'Database bucket connection established with bucket object: {bucket}')

    # Wait for API to be awake, run one simple tests to authenticate
    test_get_access_token()


def main():
    logger.info("Initializing service")
    init()
    logger.info("Service finished initializing")


if __name__ == "__main__":
    main()
