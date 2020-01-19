import requests

from app import crud
from app.core import config
from app.db.database import get_default_bucket
from app.models.user import UserCreate
from app.tests.utils.user import user_authentication_headers
from app.tests.utils.utils import get_server_api, random_lower_string


def test_get_users_superuser_me(superuser_token_headers):
    server_api = get_server_api()
    r = requests.get(
        f"{server_api}{config.API_V1_STR}/users/me", headers=superuser_token_headers
    )
    current_user = r.json()
    assert current_user
    assert current_user["disabled"] is False
    assert "superuser" in current_user["admin_roles"]
    assert current_user["username"] == config.FIRST_SUPERUSER


def test_get_users_normal_user_me(normal_user_token_headers):
    server_api = get_server_api()
    r = requests.get(
        f"{server_api}{config.API_V1_STR}/users/me", headers=normal_user_token_headers
    )
    current_user = r.json()
    assert current_user
    assert current_user["disabled"] is False
    assert "superuser" not in current_user["admin_roles"]
    assert current_user["email"] == config.EMAIL_TEST_USER


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
    bucket = get_default_bucket()
    user = crud.user.get(bucket, username=username)
    assert user.username == created_user["username"]


def test_get_existing_user(superuser_token_headers):
    server_api = get_server_api()
    username = random_lower_string()
    password = random_lower_string()
    user_in = UserCreate(username=username, email=username, password=password)
    bucket = get_default_bucket()
    user = crud.user.upsert(bucket, user_in=user_in, persist_to=1)
    r = requests.get(
        f"{server_api}{config.API_V1_STR}/users/{username}",
        headers=superuser_token_headers,
    )
    assert 200 <= r.status_code < 300
    api_user = r.json()
    user = crud.user.get(bucket, username=username)
    assert user.username == api_user["username"]


def test_create_user_existing_username(superuser_token_headers):
    server_api = get_server_api()
    username = random_lower_string()
    # username = email
    password = random_lower_string()
    user_in = UserCreate(username=username, email=username, password=password)
    bucket = get_default_bucket()
    user = crud.user.upsert(bucket, user_in=user_in, persist_to=1)
    data = {"username": username, "password": password}
    r = requests.post(
        f"{server_api}{config.API_V1_STR}/users/",
        headers=superuser_token_headers,
        json=data,
    )
    created_user = r.json()
    assert r.status_code == 400
    assert "_id" not in created_user


def test_create_user_by_normal_user(normal_user_token_headers):
    server_api = get_server_api()
    username = random_lower_string()
    password = random_lower_string()
    data = {"username": username, "password": password}
    r = requests.post(
        f"{server_api}{config.API_V1_STR}/users/", headers=normal_user_token_headers, json=data
    )
    assert r.status_code == 400


def test_retrieve_users(superuser_token_headers):
    server_api = get_server_api()
    username = random_lower_string()
    password = random_lower_string()
    user_in = UserCreate(username=username, email=username, password=password)
    bucket = get_default_bucket()
    user = crud.user.upsert(bucket, user_in=user_in, persist_to=1)

    username2 = random_lower_string()
    password2 = random_lower_string()
    user_in2 = UserCreate(username=username2, email=username2, password=password2)
    user2 = crud.user.upsert(bucket, user_in=user_in, persist_to=1)

    r = requests.get(
        f"{server_api}{config.API_V1_STR}/users/", headers=superuser_token_headers
    )
    all_users = r.json()

    assert len(all_users) > 1
    for user in all_users:
        assert "username" in user
        assert "admin_roles" in user
