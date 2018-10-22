# Standard module packages
# Installed packages
from couchbase.bucket import Bucket
from couchbase.n1ql import N1QLQuery

# Install app code
from app.core.config import COUCHBASE_BUCKET_NAME
from app.core.security import get_password_hash, verify_password
from app.models.user import User
from app.models.role import RoleEnum
from app.models.config import USERPROFILE_DOC_TYPE
from app.crud.utils import get_all_documents_by_type
# Types
from typing import Sequence, Mapping, List  # noqa


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


def create_user(
    bucket: Bucket,
    name: str,
    password: str,
    human_name: str = None,
    email: str = None,
    admin_roles: Sequence[RoleEnum] = [],
    admin_channels: Sequence[str] = [],
    disabled=False,
):
    user_doc_id = get_user_doc_id(name)
    store_password = get_password_hash(password)
    user = User(
        name=name,
        password=store_password,
        human_name=human_name,
        email=email,
        admin_roles=admin_roles,
        admin_channels=admin_channels,
        disabled=disabled,
    )
    doc_data = user.json_dict()
    bucket.insert(user_doc_id, doc_data)
    user = get_user(bucket, name)
    return user


def create_or_get_user(
    bucket: Bucket,
    name: str,
    password: str,
    human_name: str = None,
    email: str = None,
    admin_roles: Sequence[RoleEnum] = [],
    admin_channels: Sequence[str] = [],
    disabled=False,
):
    user = get_user(bucket, name)
    if user:
        return user
    user = create_user(
        bucket,
        name,
        password,
        human_name=human_name,
        email=email,
        admin_roles=admin_roles,
        admin_channels=admin_channels,
        disabled=disabled,
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
    doc_results = get_all_documents_by_type(bucket, doc_type=USERPROFILE_DOC_TYPE, skip=skip, limit=limit)
    users = []
    for item in doc_results:
        data = item[COUCHBASE_BUCKET_NAME]
        doc_id = item["id"]
        user = User(**data)
        user.Meta.key = doc_id
        users.append(user)
    return users
