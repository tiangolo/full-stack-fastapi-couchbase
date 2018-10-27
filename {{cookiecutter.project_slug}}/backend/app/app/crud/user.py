# Standard module packages
import logging
# Installed packages
from couchbase.bucket import Bucket
from couchbase.n1ql import N1QLQuery
import requests

# Install app code
from app.core.config import (
    COUCHBASE_BUCKET_NAME,
    COUCHBASE_SYNC_GATEWAY_DATABASE,
    COUCHBASE_SYNC_GATEWAY_HOST,
    COUCHBASE_SYNC_GATEWAY_PORT,
    COUCHBASE_SYNC_GATEWAY_USER,
    COUCHBASE_SYNC_GATEWAY_PASSWORD,
)
from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.models.role import RoleEnum
from app.models.config import USERPROFILE_DOC_TYPE
from app.crud.utils import get_all_documents_by_type, ensure_enums_to_strs

# Types
from typing import Sequence, Mapping, List, Union  # noqa
from enum import Enum

def get_user_doc_id(name):
    return f"userprofile::{name}"


def get_user(bucket: Bucket, name: str):
    doc_id = get_user_doc_id(name)
    result = bucket.get(doc_id, quiet=True)
    if not result.value:
        return result.value
    user = User(**result.value)
    user.Meta.key = result.key
    return user


def upsert_sync_gateway_user(
    name: str,
    password: str,
    *,
    admin_channels: Sequence[Union[Enum, str]] = [],
    admin_roles: Sequence[Union[RoleEnum, str]] = [],
    disabled=False,
    email: str = None,
):
    url = f"http://{COUCHBASE_SYNC_GATEWAY_HOST}:{COUCHBASE_SYNC_GATEWAY_PORT}/{COUCHBASE_SYNC_GATEWAY_DATABASE}/_user/{name}"
    data = {
        "name": name,
        "password": password,
        "admin_channels": ensure_enums_to_strs(admin_channels),
        "admin_roles": ensure_enums_to_strs(admin_roles),
        "email": email,
        "disabled": disabled,
    }
    response = requests.put(url, json=data)
    print(response)
    print(response.text)
    logging.info(response)
    logging.info(response.text)
    return response.status_code == 200 or response.status_code == 201


def upsert_user_in_db(
    bucket: Bucket,
    name: str,
    password: str,
    *,
    admin_channels: Sequence[Union[Enum, str]] = [],
    admin_roles: Sequence[Union[RoleEnum, str]] = [],
    disabled=False,
    email: str = None,
    human_name: str = None,
):
    user_doc_id = get_user_doc_id(name)
    store_password = get_password_hash(password)
    user = User(
        name=name,
        password=store_password,
        human_name=human_name,
        email=email,
        admin_roles=ensure_enums_to_strs(admin_roles),
        admin_channels=ensure_enums_to_strs(admin_channels),
        disabled=disabled,
    )
    doc_data = user.json_dict()
    bucket.upsert(user_doc_id, doc_data)
    user = get_user(bucket, name)
    return user


def upsert_user(
    bucket: Bucket,
    name: str,
    password: str,
    *,
    admin_channels: Sequence[Union[Enum, str]] = [],
    admin_roles: Sequence[Union[RoleEnum, str]] = [],
    disabled=False,
    email: str = None,
    human_name: str = None,
):
    user = upsert_user_in_db(
        bucket,
        name,
        password,
        admin_channels=admin_channels,
        admin_roles=admin_roles,
        disabled=disabled,
        email=email,
        human_name=human_name,
    )
    assert upsert_sync_gateway_user(
        name,
        password,
        admin_channels=admin_channels,
        admin_roles=admin_roles,
        disabled=disabled,
        email=email,
    )
    return user

def create_or_get_user(
    bucket: Bucket,
    name: str,
    password: str,
    *,
    admin_channels: Sequence[Union[Enum, str]] = [],
    admin_roles: Sequence[Union[RoleEnum, str]] = [],
    disabled=False,
    email: str = None,
    human_name: str = None,
):
    user = get_user(bucket, name)
    if user:
        return user
    user = upsert_user(
        bucket,
        name,
        password,
        admin_channels=admin_channels,
        admin_roles=admin_roles,
        disabled=disabled,
        email=email,
        human_name=human_name,
    )
    return user


def authenticate_user(bucket: Bucket, name: str, password: str):
    user = get_user(bucket, name)
    if not user:
        return False
    if not verify_password(password, user.password):
        return False
    return user


def check_if_user_is_active(user: User):
    return not user.disabled


def check_if_user_is_superuser(user: User):
    return RoleEnum.superuser.value in user.admin_roles


def get_users(bucket: Bucket, *, skip=0, limit=100):
    doc_results = get_all_documents_by_type(
        bucket, doc_type=USERPROFILE_DOC_TYPE, skip=skip, limit=limit
    )
    users = []
    for item in doc_results:
        data = item[COUCHBASE_BUCKET_NAME]
        doc_id = item["id"]
        user = User(**data)
        user.Meta.key = doc_id
        users.append(user)
    return users
