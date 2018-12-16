import logging

import requests
from requests.auth import HTTPBasicAuth

from app.core.config import (
    COUCHBASE_FTS_MEMORY_QUOTA_MB,
    COUCHBASE_INDEX_MEMORY_QUOTA_MB,
    COUCHBASE_MEMORY_QUOTA_MB,
    COUCHBASE_N1QL_TIMEOUT_SECS,
    COUCHBASE_OPERATION_TIMEOUT_SECS,
)

COUCHBASE_DEFAULT_USER = "Administrator"
COUCHBASE_DEFAULT_PASSWORD = "password"  # noqa

COUCHBASE_DEFAULT_DATASET = "travel-sample"

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

max_tries = 60 * 5  # 5 minutes
wait_seconds = 1


def get_cluster_http_url(host="couchbase", port="8091"):
    cluster_url = f"http://{host}:{port}"
    return cluster_url


def get_cluster_couchbase_url(
    host="couchbase",
    port="8091",
    fetch_mutation_tokens="1",
    operation_timeout=f"{COUCHBASE_OPERATION_TIMEOUT_SECS}",
    n1ql_timeout=f"{COUCHBASE_N1QL_TIMEOUT_SECS}",
):
    # fetch_mutation_tokens becomes required to be able to do persist_to=1: https://forums.couchbase.com/t/couchbase-returns-error-on-success/14196/2
    # ref: https://docs.couchbase.com/c-sdk/2.10/client-settings.html#settings-list
    cluster_url = f"couchbase://{host}:{port}?fetch_mutation_tokens={fetch_mutation_tokens}&operation_timeout={operation_timeout}&n1ql_timeout={n1ql_timeout}"
    return cluster_url


def get_allowed_username(username):
    chars_to_remove = '()<>@,;:"/\[]?={}'
    modified_username = username
    for char in chars_to_remove:
        modified_username = modified_username.replace(char, "-")
    return modified_username


def is_couchbase_ready(cluster_url):
    r = requests.get(cluster_url)
    return r.status_code == 200


def setup_couchbase_services(*, cluster_url, username, password):
    auth = HTTPBasicAuth(username, password)
    url = f"{cluster_url}/node/controller/setupServices"
    r = requests.post(url, data={"services": "kv,index,fts,n1ql"}, auth=auth)
    return (
        r.status_code == 200
        or "cannot change node services after cluster is provisioned" in r.text
    )


def setup_memory_quota(
    *,
    cluster_url,
    username,
    password,
    memory_quota_mb="256",
    index_memory_quota_mb="256",
    fts_memory_quota_mb="256",
):
    auth = HTTPBasicAuth(username, password)
    url = f"{cluster_url}/pools/default"
    r = requests.post(
        url,
        data={
            "memoryQuota": memory_quota_mb,
            "indexMemoryQuota": index_memory_quota_mb,
            "ftsMemoryQuota": fts_memory_quota_mb,
        },
        auth=auth,
    )
    return r.status_code == 200


def setup_index_storage(*, cluster_url, username, password):
    url = f"{cluster_url}/settings/indexes"
    auth = HTTPBasicAuth(username, password)
    r = requests.post(url, data={"storageMode": "forestdb"}, auth=auth)
    return r.status_code == 200


def setup_couchbase_username_password(*, cluster_url, username, password):
    url = f"{cluster_url}/settings/web"
    auth = HTTPBasicAuth(COUCHBASE_DEFAULT_USER, COUCHBASE_DEFAULT_PASSWORD)
    r = requests.post(
        url,
        data={"username": username, "password": password, "port": "SAME"},
        auth=auth,
    )
    return r.status_code == 200


def check_couchbase_username_password(*, cluster_url, username, password):
    url = f"{cluster_url}/settings/web"
    auth = HTTPBasicAuth(username, password)
    r = requests.get(url, auth=auth)
    return r.status_code == 200


def ensure_couchbase_username_password(*, cluster_url, username, password):
    if setup_couchbase_username_password(
        cluster_url=cluster_url, username=username, password=password
    ):
        return True
    return check_couchbase_username_password(
        cluster_url=cluster_url, username=username, password=password
    )


def import_couchbase_default_data(*, cluster_url, username, password):
    url = f"{cluster_url}/sampleBuckets/install"
    auth = HTTPBasicAuth(username, password)
    r = requests.post(url, json=["travel-sample"], auth=auth)
    return (
        r.status_code == 202
        or f"Sample bucket {COUCHBASE_DEFAULT_DATASET} is already loaded." in r.text
    )


def is_bucket_created(*, cluster_url, username, password, bucket_name):
    url = f"{cluster_url}/pools/default/buckets/{bucket_name}"
    auth = HTTPBasicAuth(username, password)
    r = requests.get(url, auth=auth)
    return r.status_code == 200


def create_bucket(
    *,
    cluster_url,
    username,
    password,
    bucket_name,
    ram_quota_mb=100,
    bucket_type="couchbase",
):
    url = f"{cluster_url}/pools/default/buckets"
    auth = HTTPBasicAuth(username, password)
    data = {"name": bucket_name, "ramQuotaMB": ram_quota_mb, "bucketType": bucket_type}
    r = requests.post(url, data=data, auth=auth)
    return r.status_code == 202


def ensure_create_bucket(
    *,
    cluster_url,
    username,
    password,
    bucket_name,
    ram_quota_mb=100,
    bucket_type="couchbase",
):
    if is_bucket_created(
        cluster_url=cluster_url,
        username=username,
        password=password,
        bucket_name=bucket_name,
    ):
        return True
    return create_bucket(
        cluster_url=cluster_url,
        username=username,
        password=password,
        bucket_name=bucket_name,
        ram_quota_mb=ram_quota_mb,
        bucket_type=bucket_type,
    )


def is_couchbase_user_created(*, cluster_url, username, password, new_user_id):
    url = f"{cluster_url}/settings/rbac/users/local/{new_user_id}"
    auth = HTTPBasicAuth(username, password)
    r = requests.get(url, auth=auth)
    return r.status_code == 200


def create_couchbase_user(
    *, cluster_url, username, password, new_user_id, new_user_password
):
    url = f"{cluster_url}/settings/rbac/users/local/{new_user_id}"
    auth = HTTPBasicAuth(username, password)
    data = {
        "name": "",
        "roles": "ro_admin,bucket_full_access[*]",
        "password": new_user_password,
    }
    r = requests.put(url, data=data, auth=auth)
    return r.status_code == 200


def ensure_create_couchbase_user(
    *, cluster_url, username, password, new_user_id, new_user_password
):
    if is_couchbase_user_created(
        cluster_url=cluster_url,
        username=username,
        password=password,
        new_user_id=new_user_id,
    ):
        return True
    return create_couchbase_user(
        cluster_url=cluster_url,
        username=username,
        password=password,
        new_user_id=new_user_id,
        new_user_password=new_user_password,
    )


def config_couchbase(
    *, username, password, enterprise=False, host="couchbase", port="8091"
):
    allowed_username = get_allowed_username(username)
    assert (
        username == allowed_username
    ), f"Not a valid username: {username}, a valid one would be {allowed_username}"
    cluster_url = get_cluster_http_url(host=host, port=port)
    logger.info("before is_couchbase_ready")
    assert is_couchbase_ready(cluster_url)
    logger.info("after is_couchbase_ready")

    logger.info("before setup_couchbase_services")
    assert setup_couchbase_services(
        cluster_url=cluster_url,
        username=COUCHBASE_DEFAULT_USER,
        password=COUCHBASE_DEFAULT_PASSWORD,
    ) or setup_couchbase_services(
        cluster_url=cluster_url, username=username, password=password
    )
    logger.info("after setup_couchbase_services")

    logger.info("before setup_memory_quota")
    assert setup_memory_quota(
        cluster_url=cluster_url,
        username=COUCHBASE_DEFAULT_USER,
        password=COUCHBASE_DEFAULT_PASSWORD,
        memory_quota_mb=COUCHBASE_MEMORY_QUOTA_MB,
        fts_memory_quota_mb=COUCHBASE_FTS_MEMORY_QUOTA_MB,
        index_memory_quota_mb=COUCHBASE_INDEX_MEMORY_QUOTA_MB,
    ) or setup_memory_quota(
        cluster_url=cluster_url,
        username=username,
        password=password,
        memory_quota_mb=COUCHBASE_MEMORY_QUOTA_MB,
        fts_memory_quota_mb=COUCHBASE_FTS_MEMORY_QUOTA_MB,
        index_memory_quota_mb=COUCHBASE_INDEX_MEMORY_QUOTA_MB,
    )
    logger.info("after setup_memory_quota")

    if not enterprise:
        logger.info("before setup_index_storage")
        assert setup_index_storage(
            cluster_url=cluster_url,
            username=COUCHBASE_DEFAULT_USER,
            password=COUCHBASE_DEFAULT_PASSWORD,
        ) or setup_index_storage(
            cluster_url=cluster_url, username=username, password=password
        )
        logger.info("after setup_index_storage")

    logger.info("before ensure_couchbase_username_password")
    assert ensure_couchbase_username_password(
        cluster_url=cluster_url, username=username, password=password
    )
    logger.info("after ensure_couchbase_username_password")
    return True
