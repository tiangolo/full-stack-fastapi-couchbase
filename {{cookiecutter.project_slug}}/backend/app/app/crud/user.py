import requests
from couchbase.bucket import Bucket
from couchbase.n1ql import CONSISTENCY_REQUEST, N1QLQuery
from fastapi.encoders import jsonable_encoder

from app.core import config
from app.core.security import get_password_hash, verify_password
from app.models.config import USERPROFILE_DOC_TYPE
from app.models.role import RoleEnum
from app.models.user import UserCreate, UserInDB, UserSyncIn, UserUpdate

from . import utils

# Same as file name /app/app/search_index_definitions/users.json
full_text_index_name = "users"


def get_doc_id(username: str):
    return f"{USERPROFILE_DOC_TYPE}::{username}"


def get(bucket: Bucket, *, username: str):
    doc_id = get_doc_id(username)
    return utils.get_doc(bucket=bucket, doc_id=doc_id, doc_model=UserInDB)


def get_by_email(bucket: Bucket, *, email: str):
    query_str = f"SELECT *, META().id as doc_id FROM {config.COUCHBASE_BUCKET_NAME} WHERE type = $type AND email = $email;"
    q = N1QLQuery(
        query_str,
        bucket=config.COUCHBASE_BUCKET_NAME,
        type=USERPROFILE_DOC_TYPE,
        email=email,
    )
    q.consistency = CONSISTENCY_REQUEST
    doc_results = bucket.n1ql_query(q)
    users = utils.doc_results_to_model(doc_results, doc_model=UserInDB)
    if not users:
        return None
    return users[0]


def insert_sync_gateway(user: UserSyncIn):
    name = user.name
    url = f"http://{config.COUCHBASE_SYNC_GATEWAY_HOST}:{config.COUCHBASE_SYNC_GATEWAY_PORT}/{config.COUCHBASE_SYNC_GATEWAY_DATABASE}/_user/{name}"
    data = jsonable_encoder(user)
    response = requests.put(url, json=data)
    return response.status_code == 200 or response.status_code == 201


def update_sync_gateway(user: UserSyncIn):
    name = user.name
    url = f"http://{config.COUCHBASE_SYNC_GATEWAY_HOST}:{config.COUCHBASE_SYNC_GATEWAY_PORT}/{config.COUCHBASE_SYNC_GATEWAY_DATABASE}/_user/{name}"
    if user.password:
        data = jsonable_encoder(user)
    else:
        data = jsonable_encoder(user, exclude={"password"})
    response = requests.put(url, json=data)
    return response.status_code == 200 or response.status_code == 201


def upsert_in_db(bucket: Bucket, *, user_in: UserCreate, persist_to=0):
    user_doc_id = get_doc_id(user_in.username)
    passwordhash = get_password_hash(user_in.password)
    user = UserInDB(**user_in.dict(), hashed_password=passwordhash)
    doc_data = jsonable_encoder(user)
    with bucket.durability(
        persist_to=persist_to, timeout=config.COUCHBASE_DURABILITY_TIMEOUT_SECS
    ):
        bucket.upsert(user_doc_id, doc_data)
    return user


def update_in_db(bucket: Bucket, *, username: str, user_in: UserUpdate, persist_to=0):
    user_doc_id = get_doc_id(username)
    stored_user = get(bucket, username=username)
    stored_user = stored_user.copy(update=user_in.dict(skip_defaults=True))
    if user_in.password:
        passwordhash = get_password_hash(user_in.password)
        stored_user.hashed_password = passwordhash
    data = jsonable_encoder(stored_user)
    with bucket.durability(
        persist_to=persist_to, timeout=config.COUCHBASE_DURABILITY_TIMEOUT_SECS
    ):
        bucket.upsert(user_doc_id, data)
    return stored_user


def upsert(bucket: Bucket, *, user_in: UserCreate, persist_to=0):
    user = upsert_in_db(bucket, user_in=user_in, persist_to=persist_to)
    user_in_sync = UserSyncIn(**user_in.dict(), name=user_in.username)
    assert insert_sync_gateway(user_in_sync)
    return user


def update(bucket: Bucket, *, username: str, user_in: UserUpdate, persist_to=0):
    user = update_in_db(
        bucket, username=username, user_in=user_in, persist_to=persist_to
    )
    user_in_sync_data = user.dict()
    user_in_sync_data.update({"name": user.username})
    if user_in.password:
        user_in_sync_data.update({"password": user_in.password})
    user_in_sync = UserSyncIn(**user_in_sync_data)
    assert update_sync_gateway(user_in_sync)
    return user


def authenticate(bucket: Bucket, *, username: str, password: str):
    user = get(bucket, username=username)
    if not user:
        return None
    if not verify_password(password, user.hashed_password):
        return None
    return user


def is_active(user: UserInDB):
    return not user.disabled


def is_superuser(user: UserInDB):
    return RoleEnum.superuser.value in utils.ensure_enums_to_strs(
        user.admin_roles or []
    )


def get_multi(bucket: Bucket, *, skip=0, limit=100):
    users = utils.get_docs(
        bucket=bucket,
        doc_type=USERPROFILE_DOC_TYPE,
        doc_model=UserInDB,
        skip=skip,
        limit=limit,
    )
    return users


def search(bucket: Bucket, *, query_string: str, skip=0, limit=100):
    users = utils.search_get_docs(
        bucket=bucket,
        query_string=query_string,
        index_name=full_text_index_name,
        doc_model=UserInDB,
        doc_type=USERPROFILE_DOC_TYPE,
        skip=skip,
        limit=limit,
    )
    return users


def search_get_search_results_to_docs(
    bucket: Bucket, *, query_string: str, skip=0, limit=100
):
    users = utils.search_by_type_get_results_to_docs(
        bucket=bucket,
        query_string=query_string,
        index_name=full_text_index_name,
        doc_type=USERPROFILE_DOC_TYPE,
        doc_model=UserInDB,
        skip=skip,
        limit=limit,
    )
    return users
