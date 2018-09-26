# Standard module packages
import base64

# Installed packages
from requests.exceptions import HTTPError
from cloudant.client import CouchDB

# Install app code
from app.db.database import get_client, get_db_app, get_db_users
from app.db.roles import add_user_to_db_members, add_role_to_db_admins
from app.core import config

# Types
from typing import Sequence, Mapping  # noqa
from cloudant.database import CloudantDatabase  # noqa
from cloudant.document import Document  # noqa


def get_user_id(username):
    return f"org.couchdb.user:{username}"


# get_user_id has a test_get_user_id


def create_or_get_user(
    username, password, is_superuser=False, db_users=None, client=None
) -> Document:
    roles = ["active"]
    if is_superuser:
        roles.append("superuser")
    user = get_user(username, db_users=db_users, client=client)
    if not user:
        if not db_users:
            db_users = get_db_users(client)
        db_users.create_document(
            {
                "_id": get_user_id(username),
                "name": username,
                "password": password,
                "type": "user",
                "roles": roles,
            }
        )  # type: Document
        user = get_user(username, db_users=db_users, client=client)
        # Fetch to do not have the password
        user.fetch()
    return user


# create_or_get_user has a test


def get_user(username, db_users=None, client=None):
    user_id = get_user_id(username)
    try:
        if client is None:
            client = get_client()
        # Force a possible session renew, as the driver doesn't
        # renew a session when it gets 404 errors, while they
        # could be an expired session and not that the user
        # doesn't exist
        client.session()
        if not db_users:
            db_users = get_db_users(client)
        doc = db_users[user_id]
        # doc.fetch()
        return doc
    except KeyError:
        return None


# get_user has two tests: test_get_user and test_get_user_different_usernames


def get_database_id_for_user(username: str) -> str:
    hex_user = "".join([hex(ord(c))[2:] for c in username])
    return f"userdb-{hex_user}"


# get_database_id_for_user has a test get_database_id_for_user


def get_database_for_user(username: str, client=None) -> CloudantDatabase:
    if not client:
        client = get_client()
    return client.create_database(get_database_id_for_user(username))


# get_database_for user is covered by test_create_db_for_user


def create_user_with_default_db(username, password, db_users=None, client=None):
    user = create_or_get_user(username, password, db_users=db_users, client=client)
    database = get_database_for_user(username, client=client)
    add_user_to_db_members(username, database)
    add_role_to_db_admins(config.ROLE_SUPERUSER, database)
    database.create_query_index(
        design_document_id="type_timestamp",
        index_name="type_timestamp",
        fields=[{"type": "desc"}, {"timestamp": "desc"}],
    )
    return user, database


# create_user_with_default_db has a test in test-roles and in test-user


def authenticate_user(username, password, db_users=None, client=None):
    try:
        # username = 'test@example.com'
        # password = 'testexample'
        user_client = CouchDB(username, password, url=config.COUCHDB_URL, connect=True)
        user_client.disconnect()
        user = get_user(username, db_users=db_users, client=client)
        # user.fetch()
        return user
    except HTTPError:
        return False


# authenticate_user has several tests: test_authenticate_user, test_not_authenticate_user


def check_if_username_is_active(username, db_users=None, client=None):
    user = get_user(username, db_users=db_users, client=client)
    return "active" in user.get("roles", []) if user else False


# check_if_username_is_active has several tests: test_check_if_username_is_active, test_check_if_username_is_active_inactive,
# test_check_if_username_is_active_inexistent


def check_if_user_is_active(user):
    return "active" in user.get("roles", []) if user else False


# check_if_user_is_active has several tests: test_check_if_user_is_active,
# test_check_if_user_is_active_inactive


def check_if_user_is_superuser(user):
    return "superuser" in user.get("roles", []) if user else False


# check_if_user_is_superuser has several tests: test_check_if_user_is_superuser,
# test_check_if_user_is_superuser_normal_user

def get_db_app_doc(_id, db_app=None, client=None):
    if not db_app:
        db_app = get_db_app()
    doc = db_app[_id]
    # doc.fetch()
    return doc
