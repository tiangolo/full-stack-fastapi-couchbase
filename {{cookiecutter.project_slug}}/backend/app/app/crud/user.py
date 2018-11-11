# Standard module packages
import logging

# Installed packages
from couchbase.bucket import Bucket
import requests

# Install app code
from app.core.config import (
    COUCHBASE_BUCKET_NAME,
    COUCHBASE_SYNC_GATEWAY_DATABASE,
    COUCHBASE_SYNC_GATEWAY_HOST,
    COUCHBASE_SYNC_GATEWAY_PORT,
)
from app.core.security import get_password_hash, verify_password
from app.models.user import UserStored, UserSyncIn, UserInCreate, UserInUpdate
from app.models.role import RoleEnum
from app.models.config import USERPROFILE_DOC_TYPE
from app.crud.utils import get_all_documents_by_type, ensure_enums_to_strs


def get_user_doc_id(name):
    return f"userprofile::{name}"


def get_user(bucket: Bucket, name: str):
    doc_id = get_user_doc_id(name)
    result = bucket.get(doc_id, quiet=True)
    if not result.value:
        return None
    print(result.value)
    user = UserStored(**result.value)
    user.Meta.key = result.key
    return user


def upsert_sync_gateway_user(user: UserSyncIn):
    name = user.name
    url = f"http://{COUCHBASE_SYNC_GATEWAY_HOST}:{COUCHBASE_SYNC_GATEWAY_PORT}/{COUCHBASE_SYNC_GATEWAY_DATABASE}/_user/{name}"

    data = user.json_dict()
    response = requests.put(url, json=data)
    print(response)
    print(response.text)
    logging.info(response)
    logging.info(response.text)
    return response.status_code == 200 or response.status_code == 201


def update_sync_gateway_user(user: UserSyncIn):
    name = user.name
    url = f"http://{COUCHBASE_SYNC_GATEWAY_HOST}:{COUCHBASE_SYNC_GATEWAY_PORT}/{COUCHBASE_SYNC_GATEWAY_DATABASE}/_user/{name}"
    if user.password:
        data = user.json_dict()
    else:
        data = user.json_dict(exclude=set(["password"]))
    response = requests.put(url, json=data)
    print(response)
    print(response.text)
    logging.info(response)
    logging.info(response.text)
    return response.status_code == 200 or response.status_code == 201


def upsert_user_in_db(bucket: Bucket, user_in: UserInCreate):
    user_doc_id = get_user_doc_id(user_in.name)
    passwordhash = get_password_hash(user_in.password)

    user = UserStored(**user_in.json_dict(), hashed_password=passwordhash)
    doc_data = user.json_dict()
    bucket.upsert(user_doc_id, doc_data)
    return user


def update_user_in_db(bucket: Bucket, user_in: UserInUpdate):
    stored_user = get_user(bucket, user_in.name)
    for field in stored_user.fields:
        print("stored field", field)
        if field in user_in.fields:
            print("input field", field)
            value_in = getattr(user_in, field)
            if value_in is not None:
                setattr(stored_user, field, value_in)
    if user_in.password:
        passwordhash = get_password_hash(user_in.password)
        stored_user.hashed_password = passwordhash
    data = stored_user.json_dict()
    bucket.upsert(stored_user.Meta.key, data)
    return stored_user


def upsert_user(bucket: Bucket, user_in: UserInCreate):
    user = upsert_user_in_db(bucket, user_in)
    user_in_sync = UserSyncIn(**user_in.json_dict())
    assert upsert_sync_gateway_user(user_in_sync)
    return user


def update_user(bucket: Bucket, user_in: UserInUpdate):
    user = update_user_in_db(bucket, user_in)
    user_in_sync = UserSyncIn(**user_in.json_dict())
    assert update_sync_gateway_user(user_in_sync)
    return user


def authenticate_user(bucket: Bucket, name: str, password: str):
    user = get_user(bucket, name)
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user


def check_if_user_is_active(user: UserStored):
    return not user.disabled


def check_if_user_is_superuser(user: UserStored):
    return RoleEnum.superuser.value in ensure_enums_to_strs(user.admin_roles)


def get_users(bucket: Bucket, *, skip=0, limit=100):
    doc_results = get_all_documents_by_type(
        bucket, doc_type=USERPROFILE_DOC_TYPE, skip=skip, limit=limit
    )
    users = []
    for item in doc_results:
        data = item[COUCHBASE_BUCKET_NAME]
        doc_id = item["id"]
        user = UserStored(**data)
        user.Meta.key = doc_id
        users.append(user)
    return users
