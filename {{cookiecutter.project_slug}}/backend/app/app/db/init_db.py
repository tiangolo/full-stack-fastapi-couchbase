import logging

from app import crud
from app.core import config
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
from app.db.full_text_search_utils import ensure_create_full_text_indexes
from app.models.role import RoleEnum
from app.models.user import UserInCreate


def init_db():
    cluster_url = get_cluster_http_url(
        host=config.COUCHBASE_HOST, port=config.COUCHBASE_PORT
    )
    logging.info("before config_couchbase")
    config_couchbase(
        username=config.COUCHBASE_USER,
        password=config.COUCHBASE_PASSWORD,
        host=config.COUCHBASE_HOST,
        port=config.COUCHBASE_PORT,
    )
    logging.info("after config_couchbase")
    # COUCHBASE_USER="Administrator"
    # COUCHBASE_PASSWORD="password"
    logging.info("before ensure_create_bucket")
    ensure_create_bucket(
        cluster_url=cluster_url,
        username=config.COUCHBASE_USER,
        password=config.COUCHBASE_PASSWORD,
        bucket_name=config.COUCHBASE_BUCKET_NAME,
        ram_quota_mb=config.COUCHBASE_MEMORY_QUOTA_MB,
    )
    logging.info("after ensure_create_bucket")
    logging.info("before get_bucket")
    bucket = get_bucket(
        config.COUCHBASE_USER,
        config.COUCHBASE_PASSWORD,
        config.COUCHBASE_BUCKET_NAME,
        host=config.COUCHBASE_HOST,
        port=config.COUCHBASE_PORT,
    )
    logging.info("after get_bucket")
    logging.info("before ensure_create_primary_index")
    ensure_create_primary_index(bucket)
    logging.info("after ensure_create_primary_index")
    logging.info("before ensure_create_type_index")
    ensure_create_type_index(bucket)
    logging.info("after ensure_create_type_index")
    logging.info("before ensure_create_full_text_indexes")
    ensure_create_full_text_indexes(
        index_dir=config.COUCHBASE_FULL_TEXT_INDEX_DEFINITIONS_DIR,
        username=config.COUCHBASE_USER,
        password=config.COUCHBASE_PASSWORD,
        host=config.COUCHBASE_HOST,
        port=config.COUCHBASE_FULL_TEXT_PORT,
    )
    logging.info("after ensure_create_full_text_indexes")
    logging.info("before ensure_create_couchbase_app_user sync")
    ensure_create_couchbase_user(
        cluster_url=cluster_url,
        username=config.COUCHBASE_USER,
        password=config.COUCHBASE_PASSWORD,
        new_user_id=config.COUCHBASE_SYNC_GATEWAY_USER,
        new_user_password=config.COUCHBASE_SYNC_GATEWAY_PASSWORD,
    )
    logging.info("after ensure_create_couchbase_app_user sync")
    logging.info("before upsert_user first superuser")
    user_in = UserInCreate(
        username=config.FIRST_SUPERUSER,
        password=config.FIRST_SUPERUSER_PASSWORD,
        email=config.FIRST_SUPERUSER,
        admin_roles=[RoleEnum.superuser],
        admin_channels=[config.FIRST_SUPERUSER],
    )
    crud.user.upsert(bucket, user_in=user_in, persist_to=1)
    logging.info("after upsert_user first superuser")
