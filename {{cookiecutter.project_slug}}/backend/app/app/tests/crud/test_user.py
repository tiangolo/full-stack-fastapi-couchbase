# App code
from app.tests.utils.utils import random_lower_string
from app.db.bucket import bucket
from app.crud.user import (
    create_user,
    create_or_get_user,
    authenticate_user,
    check_if_user_is_active,
    check_if_user_is_superuser,
    get_user,
)
from app.models.role import RoleEnum


def test_create_user():
    email = random_lower_string()
    password = random_lower_string()
    user = create_user(bucket, email, password)
    assert hasattr(user, "name")
    assert user.name == email
    assert hasattr(user, "password")
    assert hasattr(user, "type")
    assert user.type == "userprofile"


def test_not_create_user_if_exists():
    email = random_lower_string()
    password = random_lower_string()
    user = create_or_get_user(bucket, email, password)
    same_user = create_or_get_user(bucket, email, password)
    assert user.Meta.key == same_user.Meta.key
    assert user.json_dict() == same_user.json_dict()


def test_authenticate_user():
    email = random_lower_string()
    password = random_lower_string()
    user = create_or_get_user(bucket, email, password)  # noqa
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
    user = create_or_get_user(bucket, email, password)  # noqa
    is_active = check_if_user_is_active(user)
    assert is_active is True


def test_check_if_user_is_active_inactive():
    email = random_lower_string()
    password = random_lower_string()
    user = create_or_get_user(bucket, email, password, disabled=True)
    is_active = check_if_user_is_active(user)
    assert is_active is False


def test_check_if_user_is_superuser():
    email = random_lower_string()
    password = random_lower_string()
    user = create_or_get_user(bucket, email, password, admin_roles=[RoleEnum.superuser])
    is_superuser = check_if_user_is_superuser(user)
    assert is_superuser is True


def test_check_if_user_is_superuser_normal_user():
    username = random_lower_string()
    password = random_lower_string()
    user = create_or_get_user(bucket, username, password)
    is_superuser = check_if_user_is_superuser(user)
    assert is_superuser is False


def test_get_user():
    password = random_lower_string()
    username = random_lower_string()
    user = create_or_get_user(bucket, username, password)
    user_2 = get_user(bucket, username)
    assert user.Meta.key == user_2.Meta.key
    assert user.json_dict() == user_2.json_dict()

