import requests

from app import crud
from app.core import config
from app.db.database import get_default_bucket
from app.models.user import UserCreate, UserUpdate
from app.tests.utils.utils import random_lower_string, get_server_api


def user_authentication_headers(server_api, email, password):
    data = {"username": email, "password": password}

    r = requests.post(f"{server_api}{config.API_V1_STR}/login/access-token", data=data)
    response = r.json()
    auth_token = response["access_token"]
    headers = {"Authorization": f"Bearer {auth_token}"}
    return headers


def create_random_user():
    email = random_lower_string()
    password = random_lower_string()
    user_in = UserCreate(username=email, email=email, password=password)
    bucket = get_default_bucket()
    user = crud.user.upsert(bucket, user_in=user_in, persist_to=1)
    return user


def authentication_token_from_email(email):
    """
    Return a valid token for the user with given email.

    If the user doesn't exist it is created first.
    """
    password = random_lower_string()
    bucket = get_default_bucket()

    user = crud.user.get_by_email(bucket, email=email)
    if not user:
        user_in = UserCreate(username=email, email=email, password=password)
        user = crud.user.upsert(bucket, user_in=user_in, persist_to=1)
    else:
        user_in = UserUpdate(password=password)
        user = crud.user.update(bucket, user=user, user_in=user_in)

    return user_authentication_headers(get_server_api(), email, password)
