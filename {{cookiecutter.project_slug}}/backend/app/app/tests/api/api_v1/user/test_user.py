# Standard library packages
import random

# Installed packages
import requests

# App code
from app.tests.utils.utils import random_lower_string, get_server_api
from app.tests.utils.user import user_authentication_headers
from app.core import config
from app.db.utils import (
    create_or_get_user,
    get_user,
    get_database_for_user,
    get_database_id_for_user,
)


def test_get_users_superuser_me(superuser_token_headers):
    server_api = get_server_api()
    r = requests.get(
        f"{server_api}{config.API_V1_STR}/users/me", headers=superuser_token_headers
    )
    current_user = r.json()
    assert current_user
    assert "active" in current_user["roles"]
    assert "superuser" in current_user["roles"]
    assert current_user["name"] == config.FIRST_SUPERUSER


def test_create_user_new_email(superuser_token_headers):
    server_api = get_server_api()
    username = random_lower_string()
    password = random_lower_string()
    data = {"username": username, "password": password}
    r = requests.post(
        f"{server_api}{config.API_V1_STR}/users/",
        headers=superuser_token_headers,
        json=data,
    )
    assert 200 <= r.status_code < 300
    created_user = r.json()
    user = get_user(username)
    for key in created_user:
        assert user[key] == created_user[key]
    db = get_database_for_user(username)
    assert db.exists()
    sd = db.get_security_document()
    assert len(sd["admins"]["roles"]) == 1
    assert "superuser" in sd["admins"]["roles"]
    assert len(sd["members"]["names"]) == 1
    assert username in sd["members"]["names"]


def test_get_existing_user(superuser_token_headers):
    server_api = get_server_api()
    username = random_lower_string()
    password = random_lower_string()
    user = create_or_get_user(username, password)
    r = requests.get(
        f"{server_api}{config.API_V1_STR}/users/{username}",
        headers=superuser_token_headers,
    )
    assert 200 <= r.status_code < 300
    api_user = r.json()
    for key in api_user:
        assert user[key] == api_user[key]


def test_create_user_existing_username(superuser_token_headers):
    server_api = get_server_api()
    username = random_lower_string()
    # username = email
    password = random_lower_string()
    user = create_or_get_user(username, password)  # noqa
    data = {"username": username, "password": password}
    r = requests.post(
        f"{server_api}{config.API_V1_STR}/users/",
        headers=superuser_token_headers,
        json=data,
    )
    created_user = r.json()
    assert r.status_code == 400
    assert "_id" not in created_user


def test_create_user_by_normal_user(superuser_token_headers):
    server_api = get_server_api()
    username = random_lower_string()
    password = random_lower_string()
    user = create_or_get_user(username, password)  # noqa
    user_token_headers = user_authentication_headers(server_api, username, password)
    data = {"username": username, "password": password}
    r = requests.post(
        f"{server_api}{config.API_V1_STR}/users/", headers=user_token_headers, json=data
    )
    assert r.status_code == 400


def test_retrieve_users(superuser_token_headers):
    server_api = get_server_api()
    username = random_lower_string()
    password = random_lower_string()
    user = create_or_get_user(username, password)

    username2 = random_lower_string()
    password2 = random_lower_string()
    user2 = create_or_get_user(username2, password2)

    r = requests.get(
        f"{server_api}{config.API_V1_STR}/users/", headers=superuser_token_headers
    )
    all_users = r.json()

    assert len(all_users) > 1
    for user in all_users:
        assert "_id" in user
        assert "name" in user
        assert "roles" in user
        assert "type" in user


def test_get_specific_user_database_by_id(superuser_token_headers):
    server_api = get_server_api()
    username = random_lower_string()
    password = random_lower_string()
    user = create_or_get_user(username, password)

    user_db_id = get_database_id_for_user(username)

    r = requests.get(
        f"{server_api}{config.API_V1_STR}/users/{username}/dbid",
        headers=superuser_token_headers,
    )
    response = r.json()

    assert r.status_code == 200
    assert response["msg"] == user_db_id
