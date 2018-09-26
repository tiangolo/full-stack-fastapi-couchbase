# Standard packages
import atexit

# Installed packages
# from cloudant.client import CouchDB
from app.couchdb_remote.client import RemoteCouchDB

# App code
from app.core import config


def get_client():
    return RemoteCouchDB(
        config.COUCHDB_USER,
        config.COUCHDB_PASSWORD,
        url=config.COUCHDB_URL,
        connect=True,
        auto_renew=True,
        remote=True,
    )


def get_db_app(client=None):
    if not client:
        client = get_client()
    return client.create_database("app")


def get_db_users(client=None):
    if not client:
        client = get_client()
    return client.create_database("_users")


@atexit.register
def close_client():
    client = get_client()
    client.disconnect()


def enable_cors():
    couch_cors_url = (
        config.COUCHDB_URL + "/_node/nonode@nohost/_config/httpd/enable_cors"
    )
    couch_cors_credentials_url = (
        config.COUCHDB_URL + "/_node/nonode@nohost/_config/cors/credentials"
    )
    couch_cors_origins_url = (
        config.COUCHDB_URL + "/_node/nonode@nohost/_config/cors/origins"
    )
    client = get_client()
    client.r_session.put(couch_cors_url, json="true")
    client.r_session.put(couch_cors_credentials_url, json="true")
    client.r_session.put(couch_cors_origins_url, json=config.COUCHDB_CORS_ORIGINS)


def setup_cookie():
    couch_persistent_cookies_url = (
        config.COUCHDB_URL
        + "/_node/nonode@nohost/_config/couch_httpd_auth/allow_persistent_cookies"
    )
    couch_timeout_url = (
        config.COUCHDB_URL + "/_node/nonode@nohost/_config/couch_httpd_auth/timeout"
    )
    client = get_client()
    client.r_session.put(couch_persistent_cookies_url, json="true")
    res = client.r_session.put(couch_timeout_url, json=str(config.COUCHDB_AUTH_TIMEOUT))


def enable_couch_peruser():
    couch_peruser_url = (
        config.COUCHDB_URL + "/_node/nonode@nohost/_config/couch_peruser/enable"
    )
    client = get_client()
    client.r_session.put(couch_peruser_url, json="true")
