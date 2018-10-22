import logging

import requests
from requests.auth import HTTPBasicAuth

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


def get_cluster_couchbase_url(host="couchbase", port="8091"):
    cluster_url = f"couchbase://{host}:{port}"
    return cluster_url


def get_allowed_username(username):
    chars_to_remove = '()<>@,;:"/\[]?={}'
    modified_username = username
    for char in chars_to_remove:
        modified_username = modified_username.replace(char, "-")
    return modified_username


def is_couchbase_ready(base_url):
    r = requests.get(base_url)
    return r.status_code == 200


def setup_couchbase_services(base_url, username, password):
    auth = HTTPBasicAuth(username, password)
    url = f"{base_url}/node/controller/setupServices"
    r = requests.post(
        url,
        data={"services": "kv,index,fts,n1ql", "setDefaultMemQuota": True},
        auth=auth,
    )
    return (
        r.status_code == 200
        or "cannot change node services after cluster is provisioned" in r.text
    )


def is_default_bucket_setup(base_url, username, password):
    url = f"{base_url}/pools/default/buckets"
    auth = HTTPBasicAuth(username, password)
    r = requests.get(url, auth=auth)
    return r.status_code == 200


def setup_default_bucket(base_url, username, password, ram_quota_mb=597):
    url = f"{base_url}/pools/default/buckets"
    auth = HTTPBasicAuth(username, password)
    r = requests.post(
        url, data={"name": "default", "ramQuotaMB": ram_quota_mb}, auth=auth
    )
    return r.status_code == 200


def setup_index_storage(base_url, username, password):
    url = f"{base_url}/settings/indexes"
    auth = HTTPBasicAuth(username, password)
    r = requests.post(
        url, data={"storageMode": "forestdb"}, auth=auth
    )
    return r.status_code == 200


def ensure_default_bucket_setup(base_url, username, password, ram_quota_mb=597):
    if is_default_bucket_setup(base_url, username, password):
        return True
    return setup_default_bucket(base_url, username, password, ram_quota_mb=ram_quota_mb)


def setup_couchbase_username_password(base_url, username, password):
    url = f"{base_url}/settings/web?just_validate=0"
    auth = HTTPBasicAuth(COUCHBASE_DEFAULT_USER, COUCHBASE_DEFAULT_PASSWORD)
    r = requests.post(
        url,
        data={"username": username, "password": password, "port": "SAME"},
        auth=auth,
    )
    return r.status_code == 200


def check_couchbase_username_password(base_url, username, password):
    url = f"{base_url}/settings/web"
    auth = HTTPBasicAuth(username, password)
    r = requests.get(url, auth=auth)
    return r.status_code == 200


def ensure_couchbase_username_password(base_url, username, password):
    if setup_couchbase_username_password(base_url, username, password):
        return True
    return check_couchbase_username_password(base_url, username, password)


def import_couchbase_default_data(base_url, username, password):
    url = f"{base_url}/sampleBuckets/install"
    auth = HTTPBasicAuth(username, password)
    r = requests.post(url, json=["travel-sample"], auth=auth)
    return (
        r.status_code == 202
        or f"Sample bucket {COUCHBASE_DEFAULT_DATASET} is already loaded." in r.text
    )


def config_couchbase(username, password, host="couchbase", port="8091"):
    allowed_username = get_allowed_username(username)
    assert (
        username == allowed_username
    ), f"Not a valid username: {username}, a valid one would be {allowed_username}"
    cluster_url = get_cluster_http_url(host=host, port=port)
    logger.info("before is_sandbox_ready")
    assert is_couchbase_ready(cluster_url)
    logger.info("after is_sandbox_ready")

    logger.info("before setup_sandbox_services")
    assert setup_couchbase_services(
        cluster_url, COUCHBASE_DEFAULT_USER, COUCHBASE_DEFAULT_PASSWORD
    ) or setup_couchbase_services(cluster_url, username, password)
    logger.info("after setup_sandbox_services")

    logger.info("before ensure_default_bucket_setup")
    assert ensure_default_bucket_setup(
        cluster_url, COUCHBASE_DEFAULT_USER, COUCHBASE_DEFAULT_PASSWORD
    ) or ensure_default_bucket_setup(cluster_url, username, password)
    logger.info("after ensure_default_bucket_setup")

    logger.info("before setup_index_storage")
    assert setup_index_storage(
        cluster_url, COUCHBASE_DEFAULT_USER, COUCHBASE_DEFAULT_PASSWORD
    ) or setup_index_storage(cluster_url, username, password)
    logger.info("after setup_index_storage")

    logger.info("before ensure_sandbox_username_password")
    assert ensure_couchbase_username_password(cluster_url, username, password)
    logger.info("after ensure_sandbox_username_password")
    return True
