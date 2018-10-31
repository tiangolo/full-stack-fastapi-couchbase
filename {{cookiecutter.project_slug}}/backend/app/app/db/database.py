
from couchbase import LOCKMODE_WAIT
from couchbase.cluster import Cluster
from couchbase.cluster import PasswordAuthenticator
from couchbase.admin import Admin
from couchbase.auth_domain import AuthDomain
from couchbase.exceptions import HTTPError
from app.db.couchbase_utils import get_cluster_couchbase_url
from app.core.config import (
    COUCHBASE_SYNC_GATEWAY_USER,
    COUCHBASE_SYNC_GATEWAY_PASSWORD,
    COUCHBASE_BUCKET_NAME,
)

# Types
from couchbase.bucket import Bucket


def ensure_create_bucket(
    username: str, password: str, bucket_name: str, host="couchbase", port="8091"
):
    adm = Admin(username, password, host=host, port=port)
    try:
        adm.bucket_create(bucket_name, bucket_type="couchbase")
        return True
    except HTTPError as e:
        if (
            e.objextra.value["errors"]["name"]
            == "Bucket with given name already exists"
        ):
            return True

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
    username: str, password: str, bucket_name: str, host="couchbase", port="8091"
):
    cluster = get_cluster(username, password, host=host, port=port)
    bucket: Bucket = cluster.open_bucket(bucket_name, lockmode=LOCKMODE_WAIT)
    return bucket


def ensure_create_primary_index(bucket: Bucket):
    manager = bucket.bucket_manager()
    return manager.n1ql_index_create_primary(ignore_exists=True)


def ensure_create_type_index(bucket: Bucket):
    manager = bucket.bucket_manager()
    return manager.n1ql_index_create("idx_type", ignore_exists=True, fields=["type"])


def ensure_create_couchbase_app_user(
    username: str,
    password: str,
    new_user: str,
    new_password: str,
    bucket_name: str,
    host="couchbase",
    port="8091",
):
    cluster = get_cluster(username, password, host=host, port=port)
    manager = cluster.cluster_manager()
    manager.user_upsert(
        AuthDomain.Local,
        new_user,
        new_password,
        [("bucket_full_access", bucket_name), "ro_admin"],
        new_user,
    )
