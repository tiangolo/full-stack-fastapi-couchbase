import logging

from app.core.config import (
    COUCHBASE_BUCKET_NAME,
    COUCHBASE_HOST,
    COUCHBASE_MEMORY_QUOTA_MB,
    COUCHBASE_PASSWORD,
    COUCHBASE_PORT,
    COUCHBASE_SYNC_GATEWAY_PASSWORD,
    COUCHBASE_SYNC_GATEWAY_USER,
    COUCHBASE_USER,
    FIRST_SUPERUSER,
    FIRST_SUPERUSER_PASSWORD,
)
from app.crud.user import upsert_user
from app.db.couchbase_utils import (
    config_couchbase,
    ensure_create_bucket,
    ensure_create_couchbase_user,
    get_cluster_http_url,
)
from app.db.database import (
    ensure_create_primary_index,
    ensure_create_type_index,
    get_bucket,
)
from app.models.role import RoleEnum
from app.models.user import UserInCreate


def init_db():
    cluster_url = get_cluster_http_url(host=COUCHBASE_HOST, port=COUCHBASE_PORT)
    logging.info("before config_couchbase")
    config_couchbase(
        username=COUCHBASE_USER,
        password=COUCHBASE_PASSWORD,
        host=COUCHBASE_HOST,
        port=COUCHBASE_PORT,
    )
    logging.info("after config_couchbase")
    # COUCHBASE_USER="Administrator"
    # COUCHBASE_PASSWORD="password"
    logging.info("before ensure_create_bucket")
    ensure_create_bucket(
        cluster_url=cluster_url,
        username=COUCHBASE_USER,
        password=COUCHBASE_PASSWORD,
        bucket_name=COUCHBASE_BUCKET_NAME,
        ram_quota_mb=COUCHBASE_MEMORY_QUOTA_MB,
    )
    logging.info("after ensure_create_bucket")
    logging.info("before get_bucket")
    bucket = get_bucket(
        COUCHBASE_USER,
        COUCHBASE_PASSWORD,
        COUCHBASE_BUCKET_NAME,
        host=COUCHBASE_HOST,
        port=COUCHBASE_PORT,
    )
    logging.info("after get_bucket")
    logging.info("before ensure_create_primary_index")
    ensure_create_primary_index(bucket)
    logging.info("after ensure_create_primary_index")
    logging.info("before ensure_create_type_index")
    ensure_create_type_index(bucket)
    logging.info("after ensure_create_type_index")
    logging.info("before ensure_create_couchbase_app_user sync")
    ensure_create_couchbase_user(
        cluster_url=cluster_url,
        username=COUCHBASE_USER,
        password=COUCHBASE_PASSWORD,
        new_user_id=COUCHBASE_SYNC_GATEWAY_USER,
        new_user_password=COUCHBASE_SYNC_GATEWAY_PASSWORD,
    )
    logging.info("after ensure_create_couchbase_app_user sync")
    logging.info("before upsert_user first superuser")
    in_user = UserInCreate(
        username=FIRST_SUPERUSER,
        password=FIRST_SUPERUSER_PASSWORD,
        email=FIRST_SUPERUSER,
        admin_roles=[RoleEnum.superuser],
        admin_channels=[FIRST_SUPERUSER],
    )
    upsert_user(bucket, in_user, persist_to=1)
    logging.info("after upsert_user first superuser")
