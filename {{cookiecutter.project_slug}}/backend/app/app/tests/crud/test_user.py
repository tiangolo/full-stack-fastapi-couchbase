# App code
from app.tests.utils.utils import random_lower_string
from app.db.bucket import bucket
from app.crud.user import (
    upsert_user,
    authenticate_user,
    check_if_user_is_active,
    check_if_user_is_superuser,
    get_user,
)
from app.models.role import RoleEnum
from app.models.user import UserInCreate


def test_create_user():
    email = random_lower_string()
    password = random_lower_string()
    user_in = UserInCreate(name=email, email=email, password=password)
    user = upsert_user(bucket, user_in)
    assert hasattr(user, "name")
    assert user.name == email
    assert hasattr(user, "hashed_password")
    assert hasattr(user, "type")
    assert user.type == "userprofile"


def test_authenticate_user():
    email = random_lower_string()
    password = random_lower_string()
    user_in = UserInCreate(name=email, email=email, password=password)
    user = upsert_user(bucket, user_in)
    authenticated_user = authenticate_user(bucket, email, password)
    assert authenticated_user
    assert user.Meta.key == authenticated_user.Meta.key


def test_not_authenticate_user():
    email = random_lower_string()
    password = random_lower_string()
    user = authenticate_user(bucket, email, password)
    assert user is False


def test_check_if_user_is_active():
    email = random_lower_string()
    password = random_lower_string()
    user_in = UserInCreate(name=email, email=email, password=password)
    user = upsert_user(bucket, user_in)
    is_active = check_if_user_is_active(user)
    assert is_active is True


def test_check_if_user_is_active_inactive():
    email = random_lower_string()
    password = random_lower_string()
    user_in = UserInCreate(name=email, email=email, password=password, disabled=True)
    user = upsert_user(bucket, user_in)
    is_active = check_if_user_is_active(user)
    assert is_active is False


def test_check_if_user_is_superuser():
    email = random_lower_string()
    password = random_lower_string()
    user_in = UserInCreate(name=email, email=email, password=password, admin_roles=[RoleEnum.superuser])
    user = upsert_user(bucket, user_in)
    is_superuser = check_if_user_is_superuser(user)
    assert is_superuser is True


def test_check_if_user_is_superuser_normal_user():
    username = random_lower_string()
    password = random_lower_string()
    user_in = UserInCreate(name=username, email=username, password=password)
    user = upsert_user(bucket, user_in)
    is_superuser = check_if_user_is_superuser(user)
    assert is_superuser is False


def test_get_user():
    password = random_lower_string()
    username = random_lower_string()
    user_in = UserInCreate(name=username, email=username, password=password, admin_roles=[RoleEnum.superuser])
    user = upsert_user(bucket, user_in)
    user_2 = get_user(bucket, username)
    assert user.Meta.key == user_2.Meta.key
    assert user.json_dict() == user_2.json_dict()
