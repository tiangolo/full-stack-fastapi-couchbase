from app.core.config import (
    COUCHBASE_BUCKET_NAME,
    COUCHBASE_HOST,
    COUCHBASE_N1QL_TIMEOUT_SECS,
    COUCHBASE_OPERATION_TIMEOUT_SECS,
    COUCHBASE_PASSWORD,
    COUCHBASE_PORT,
    COUCHBASE_USER,
)
from app.db.couchbase_utils import get_cluster_couchbase_url
from couchbase import LOCKMODE_WAIT
# Types
from couchbase.bucket import Bucket
from couchbase.cluster import Cluster, PasswordAuthenticator


def get_default_bucket():
    return get_bucket(
        COUCHBASE_USER,
        COUCHBASE_PASSWORD,
        COUCHBASE_BUCKET_NAME,
        host=COUCHBASE_HOST,
        port=COUCHBASE_PORT,
    )


def get_cluster(username: str, password: str, host="couchbase", port="8091"):
    # cluster_url="couchbase://couchbase"
    # username = "Administrator"
    # password = "password"
    cluster_url = get_cluster_couchbase_url(host=host, port=port)
    cluster = Cluster(cluster_url)
    authenticator = PasswordAuthenticator(username, password)
    cluster.authenticate(authenticator)
    return cluster


def get_bucket(
    username: str,
    password: str,
    bucket_name: str,
    host="couchbase",
    port="8091",
    timeout: int = COUCHBASE_OPERATION_TIMEOUT_SECS,
    n1ql_timeout: int = COUCHBASE_N1QL_TIMEOUT_SECS,
):
    cluster = get_cluster(username, password, host=host, port=port)
    bucket: Bucket = cluster.open_bucket(bucket_name, lockmode=LOCKMODE_WAIT)
    bucket.timeout = timeout
    bucket.n1ql_timeout = n1ql_timeout
    return bucket


def ensure_create_primary_index(bucket: Bucket):
    manager = bucket.bucket_manager()
    return manager.n1ql_index_create_primary(ignore_exists=True)


def ensure_create_type_index(bucket: Bucket):
    manager = bucket.bucket_manager()
    return manager.n1ql_index_create("idx_type", ignore_exists=True, fields=["type"])
