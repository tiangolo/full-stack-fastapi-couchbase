# App code
from app.tests.utils.utils import random_lower_string
from app.db.utils import (
    create_or_get_user,
    get_database_id_for_user,
    get_database_for_user,
    create_user_with_default_db,
    authenticate_user,
    check_if_username_is_active,
    check_if_user_is_active,
    check_if_user_is_superuser,
    get_user,
)
from app.db.database import get_client


def test_create_user():
    email = random_lower_string()
    password = random_lower_string()
    user = create_or_get_user(email, password)
    keys = ["_id", "_rev", "name", "roles", "type"]
    for key in keys:
        assert key in user


def test_not_create_user_if_exists():
    email = random_lower_string()
    password = random_lower_string()
    user = create_or_get_user(email, password)
    same_user = create_or_get_user(email, password)
    assert user == same_user


def test_not_create_db_for_user():
    email = random_lower_string()
    password = random_lower_string()
    user = create_or_get_user(email, password)  # noqa
    db_id = get_database_id_for_user(email)
    client = get_client()
    assert db_id not in client


def test_create_db_for_user():
    email = random_lower_string()
    password = random_lower_string()
    user = create_or_get_user(email, password)  # noqa
    db_id = get_database_id_for_user(email)
    db = get_database_for_user(email)
    sd = db.get_security_document()
    client = get_client()
    assert db_id in client.keys(remote=True)
    assert "members" not in sd
    assert "admins" not in sd


def test_create_user_with_default_db_indexes():
    email = random_lower_string()
    password = random_lower_string()
    user, db = create_user_with_default_db(email, password)
    ddoc = db.get_design_document("type_timestamp")
    index = ddoc.get_view("type_timestamp")
    fields = index["options"]["def"]["fields"]
    test_fields = [{"type": "desc"}, {"timestamp": "desc"}]
    assert fields == test_fields


def test_authenticate_user():
    email = random_lower_string()
    password = random_lower_string()
    user = create_or_get_user(email, password)  # noqa
    db_user = authenticate_user(email, password)
    keys = ["_id", "_rev", "name", "roles", "type"]
    assert db_user
    for key in keys:
        assert key in db_user


def test_not_authenticate_user():
    email = random_lower_string()
    password = random_lower_string()
    user = authenticate_user(email, password)
    assert user is False


def test_check_if_username_is_active():
    email = random_lower_string()
    password = random_lower_string()
    user = create_or_get_user(email, password)  # noqa
    is_active = check_if_username_is_active(email)
    assert is_active is True


def test_check_if_username_is_active_inactive():
    email = random_lower_string()
    password = random_lower_string()
    user = create_or_get_user(email, password)
    user["roles"].remove("active")
    user.save()
    is_active = check_if_username_is_active(email)
    assert is_active is False


def test_check_if_username_is_active_inexistent():
    email = random_lower_string()
    is_active = check_if_username_is_active(email)
    assert is_active is False


def test_check_if_user_is_active():
    email = random_lower_string()
    password = random_lower_string()
    user = create_or_get_user(email, password)  # noqa
    is_active = check_if_user_is_active(user)
    assert is_active is True


def test_check_if_user_is_active_inactive():
    email = random_lower_string()
    password = random_lower_string()
    user = create_or_get_user(email, password)
    user["roles"].remove("active")
    user.save()
    is_active = check_if_user_is_active(user)
    assert is_active is False


def test_check_if_user_is_superuser():
    email = random_lower_string()
    password = random_lower_string()
    user = create_or_get_user(email, password, is_superuser=True)
    is_superuser = check_if_user_is_superuser(user)
    assert is_superuser is True


def test_check_if_user_is_superuser_normal_user():
    username = random_lower_string()
    password = random_lower_string()
    user = create_or_get_user(username, password)
    is_superuser = check_if_user_is_superuser(user)
    assert is_superuser is False


def test_get_user_different_usernames():
    email = random_lower_string()
    password = random_lower_string()
    username = random_lower_string()
    user = create_or_get_user(email, password)
    user_2 = get_user(username)
    assert user != user_2


def test_get_user():
    password = random_lower_string()
    username = random_lower_string()
    user = create_or_get_user(username, password)
    user_2 = get_user(username)
    assert user == user_2
