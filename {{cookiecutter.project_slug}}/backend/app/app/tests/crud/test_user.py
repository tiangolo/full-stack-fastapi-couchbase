from fastapi.encoders import jsonable_encoder

from app import crud
from app.db.database import get_default_bucket
from app.models.role import RoleEnum
from app.models.user import UserInCreate
from app.tests.utils.utils import random_lower_string


def test_create_user():
    email = random_lower_string()
    password = random_lower_string()
    user_in = UserInCreate(username=email, email=email, password=password)
    bucket = get_default_bucket()
    user = crud.user.upsert(bucket, user_in=user_in, persist_to=1)
    assert hasattr(user, "username")
    assert user.username == email
    assert hasattr(user, "hashed_password")
    assert hasattr(user, "type")
    assert user.type == "userprofile"


def test_authenticate_user():
    email = random_lower_string()
    password = random_lower_string()
    user_in = UserInCreate(username=email, email=email, password=password)
    bucket = get_default_bucket()
    user = crud.user.upsert(bucket, user_in=user_in, persist_to=1)
    authenticated_user = crud.user.authenticate(
        bucket, username=user_in.username, password=password
    )
    assert authenticated_user
    assert user.username == authenticated_user.username


def test_not_authenticate_user():
    email = random_lower_string()
    password = random_lower_string()
    bucket = get_default_bucket()
    user = crud.user.authenticate(bucket, username=email, password=password)
    assert user is None


def test_check_if_user_is_active():
    email = random_lower_string()
    password = random_lower_string()
    user_in = UserInCreate(username=email, email=email, password=password)
    bucket = get_default_bucket()
    user = crud.user.upsert(bucket, user_in=user_in, persist_to=1)
    is_active = crud.user.is_active(user)
    assert is_active is True


def test_check_if_user_is_active_inactive():
    email = random_lower_string()
    password = random_lower_string()
    user_in = UserInCreate(
        username=email, email=email, password=password, disabled=True
    )
    bucket = get_default_bucket()
    user = crud.user.upsert(bucket, user_in=user_in, persist_to=1)
    is_active = crud.user.is_active(user)
    assert is_active is False


def test_check_if_user_is_superuser():
    email = random_lower_string()
    password = random_lower_string()
    user_in = UserInCreate(
        username=email, email=email, password=password, admin_roles=[RoleEnum.superuser]
    )
    bucket = get_default_bucket()
    user = crud.user.upsert(bucket, user_in=user_in, persist_to=1)
    is_superuser = crud.user.is_superuser(user)
    assert is_superuser is True


def test_check_if_user_is_superuser_normal_user():
    username = random_lower_string()
    password = random_lower_string()
    user_in = UserInCreate(username=username, email=username, password=password)
    bucket = get_default_bucket()
    user = crud.user.upsert(bucket, user_in=user_in, persist_to=1)
    is_superuser = crud.user.is_superuser(user)
    assert is_superuser is False


def test_get_user():
    password = random_lower_string()
    username = random_lower_string()
    user_in = UserInCreate(
        username=username,
        email=username,
        password=password,
        admin_roles=[RoleEnum.superuser],
    )
    bucket = get_default_bucket()
    user = crud.user.upsert(bucket, user_in=user_in, persist_to=1)
    user_2 = crud.user.get(bucket, username=username)
    assert user.username == user_2.username
    assert jsonable_encoder(user) == jsonable_encoder(user_2)
