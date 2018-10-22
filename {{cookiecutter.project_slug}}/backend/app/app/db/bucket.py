from app.db.database import get_bucket
from app.core.config import (
    COUCHBASE_USER,
    COUCHBASE_PASSWORD,
    COUCHBASE_BUCKET_NAME,
    COUCHBASE_HOST,
    COUCHBASE_PORT,
)

bucket = get_bucket(
    COUCHBASE_USER,
    COUCHBASE_PASSWORD,
    COUCHBASE_BUCKET_NAME,
    host=COUCHBASE_HOST,
    port=COUCHBASE_PORT,
)
