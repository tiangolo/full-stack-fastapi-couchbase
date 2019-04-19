import requests

from app import crud
from app.core import config
from app.db.database import get_default_bucket
from app.models.user import UserCreate
from app.tests.utils.utils import random_lower_string


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
