import requests
from couchbase.bucket import Bucket
from couchbase.n1ql import CONSISTENCY_REQUEST, N1QLQuery
from fastapi.encoders import jsonable_encoder

from app.core.config import (
    COUCHBASE_BUCKET_NAME,
    COUCHBASE_DURABILITY_TIMEOUT_SECS,
    COUCHBASE_SYNC_GATEWAY_DATABASE,
    COUCHBASE_SYNC_GATEWAY_HOST,
    COUCHBASE_SYNC_GATEWAY_PORT,
)
from app.core.security import get_password_hash, verify_password
from app.crud.utils import (
    ensure_enums_to_strs,
    generate_new_id,
    get_all_documents_by_type,
    get_doc,
    get_docs,
    results_to_model,
    search_results_by_type,
)
from app.models.config import USERPROFILE_DOC_TYPE
from app.models.role import RoleEnum
from app.models.user import UserInCreate, UserInDB, UserInUpdate, UserSyncIn


full_text_index_name = "users"


def get_user_doc_id(username):
    return f"userprofile::{username}"


def get_user(bucket: Bucket, username: str):
    doc_id = get_user_doc_id(username)
    return get_doc(bucket=bucket, doc_id=doc_id, doc_model=UserInDB)


def get_user_by_email(bucket: Bucket, email: str):
    query_str = f"SELECT *, META().id as doc_id FROM {COUCHBASE_BUCKET_NAME} WHERE type = $type AND email = $email;"
    q = N1QLQuery(
        query_str, bucket=COUCHBASE_BUCKET_NAME, type=USERPROFILE_DOC_TYPE, email=email
    )
    q.consistency = CONSISTENCY_REQUEST
    doc_results = bucket.n1ql_query(q)
    users = results_to_model(doc_results, doc_model=UserInDB)
    if not users:
        return None
    return users[0]


def insert_sync_gateway_user(user: UserSyncIn):
    name = user.name
    url = f"http://{COUCHBASE_SYNC_GATEWAY_HOST}:{COUCHBASE_SYNC_GATEWAY_PORT}/{COUCHBASE_SYNC_GATEWAY_DATABASE}/_user/{name}"

    data = jsonable_encoder(user)
    response = requests.put(url, json=data)
    return response.status_code == 200 or response.status_code == 201


def update_sync_gateway_user(user: UserSyncIn):
    name = user.name
    url = f"http://{COUCHBASE_SYNC_GATEWAY_HOST}:{COUCHBASE_SYNC_GATEWAY_PORT}/{COUCHBASE_SYNC_GATEWAY_DATABASE}/_user/{name}"
    if user.password:
        data = jsonable_encoder(user)
    else:
        data = jsonable_encoder(user, exclude={"password"})
    response = requests.put(url, json=data)
    return response.status_code == 200 or response.status_code == 201


def upsert_user_in_db(bucket: Bucket, user_in: UserInCreate, persist_to=0):
    user_doc_id = get_user_doc_id(user_in.username)
    passwordhash = get_password_hash(user_in.password)

    user = UserInDB(**user_in.dict(), hashed_password=passwordhash)
    doc_data = jsonable_encoder(user)
    with bucket.durability(
        persist_to=persist_to, timeout=COUCHBASE_DURABILITY_TIMEOUT_SECS
    ):
        bucket.upsert(user_doc_id, doc_data)
    return user


def update_user_in_db(bucket: Bucket, user_in: UserInUpdate, persist_to=0):
    user_doc_id = get_user_doc_id(user_in.username)
    stored_user = get_user(bucket, username=user_in.username)
    for field in stored_user.fields:
        if field in user_in.fields:
            value_in = getattr(user_in, field)
            if value_in is not None:
                setattr(stored_user, field, value_in)
    if user_in.password:
        passwordhash = get_password_hash(user_in.password)
        stored_user.hashed_password = passwordhash
    data = jsonable_encoder(stored_user)
    with bucket.durability(
        persist_to=persist_to, timeout=COUCHBASE_DURABILITY_TIMEOUT_SECS
    ):
        bucket.upsert(user_doc_id, data)
    return stored_user


def upsert_user(bucket: Bucket, user_in: UserInCreate, persist_to=0):
    user = upsert_user_in_db(bucket, user_in, persist_to=persist_to)
    user_in_sync = UserSyncIn(**user_in.dict(), name=user_in.username)
    assert insert_sync_gateway_user(user_in_sync)
    return user


def update_user(bucket: Bucket, user_in: UserInUpdate, persist_to=0):
    user = update_user_in_db(bucket, user_in, persist_to=persist_to)
    user_in_sync_data = user.dict()
    user_in_sync_data.update({"name": user.username})
    if user_in.password:
        user_in_sync_data.update({"password": user_in.password})
    user_in_sync = UserSyncIn(**user_in_sync_data)
    assert update_sync_gateway_user(user_in_sync)
    return user


def authenticate_user(bucket: Bucket, name: str, password: str):
    user = get_user(bucket, name)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def check_if_user_is_active(user: UserInDB):
    return not user.disabled


def check_if_user_is_superuser(user: UserInDB):
    return RoleEnum.superuser.value in ensure_enums_to_strs(user.admin_roles)


def get_users(bucket: Bucket, *, skip=0, limit=100):
    users = get_docs(
        bucket=bucket,
        doc_type=USERPROFILE_DOC_TYPE,
        doc_model=UserInDB,
        skip=skip,
        limit=limit,
    )
    return users

def search_user_docs(bucket: Bucket, *, query_string: str, skip=0, limit=100):
    users = search_docs(
        bucket=bucket,
        query_string=query_string,
        index_name=full_text_index_name,
        doc_model=UserInDB,
        skip=skip,
        limit=limit,
    )
    return users

def search_users(bucket: Bucket, *, query_string: str, skip=0, limit=100):
    users = search_results_by_type(
        bucket=bucket,
        query_string=query_string,
        index_name=full_text_index_name,
        doc_type=USERPROFILE_DOC_TYPE,
        doc_model=UserInDB,
        skip=skip,
        limit=limit,
    )
    return users
