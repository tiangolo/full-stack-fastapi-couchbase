# App code
from app.tests.utils.utils import random_lower_string
from app.core import config
from app.db.database import get_client
from app.db.utils import create_or_get_user, create_user_with_default_db
from app.db.roles import (
    add_user_to_db_members,
    add_user_to_db_admins,
    add_role_to_db_admins,
    add_role_to_db_members,
)


def test_add_user_to_db_members():
    client = get_client()
    db = client.create_database(random_lower_string())
    email = random_lower_string()
    password = random_lower_string()
    user = create_or_get_user(email, password)  # noqa
    add_user_to_db_members(email, db)
    sd = db.get_security_document()
    assert "members" in sd
    assert "admins" not in sd
    assert email in sd["members"]["names"]


def test_add_user_to_db_admins():
    client = get_client()
    db = client.create_database(random_lower_string())
    email = random_lower_string()
    password = random_lower_string()
    user = create_or_get_user(email, password)  # noqa
    add_user_to_db_admins(email, db)
    sd = db.get_security_document()
    assert "admins" in sd
    assert "members" not in sd
    assert email in sd["admins"]["names"]


def test_add_role_to_db_members():
    client = get_client()
    db = client.create_database(random_lower_string())
    role = "test"
    add_role_to_db_members(role, db)
    sd = db.get_security_document()
    assert "members" in sd
    assert "admins" not in sd
    assert role in sd["members"]["roles"]


def test_add_role_to_db_admins():
    client = get_client()
    db = client.create_database(random_lower_string())
    role = "test"
    add_role_to_db_admins(role, db)
    sd = db.get_security_document()
    assert "members" not in sd
    assert "admins" in sd
    assert role in sd["admins"]["roles"]


def test_create_user_with_default_db_security():
    email = random_lower_string()
    password = random_lower_string()
    user, db = create_user_with_default_db(email, password)
    security_dict = db.get_security_document()
    # Test roles and security
    assert "members" in security_dict
    assert "admins" in security_dict
    assert email in security_dict["members"]["names"]
    assert "names" not in security_dict["admins"]
    assert config.ROLE_SUPERUSER in security_dict["admins"]["roles"]
