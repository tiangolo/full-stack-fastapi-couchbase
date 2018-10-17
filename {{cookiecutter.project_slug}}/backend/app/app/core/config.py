import os


def getenv_boolean(var_name, default_value=False):
    result = default_value
    env_value = os.getenv(var_name)
    if env_value is not None:
        result = env_value.upper() in ("TRUE", "1")
    return result


API_V1_STR = "/api/v1"

SECRET_KEY = os.getenvb(b"SECRET_KEY")
if not SECRET_KEY:
    SECRET_KEY = os.urandom(32)

ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 8  # 60 minutes * 24 hours * 8 days = 8 days

SERVER_NAME = os.getenv("SERVER_NAME")
BACKEND_CORS_ORIGINS = os.getenv("BACKEND_CORS_ORIGINS")
SENTRY_DSN = os.getenv("SENTRY_DSN")

COUCHDB_USER = os.getenv("COUCHDB_USER")
COUCHDB_PASSWORD = os.getenv("COUCHDB_PASSWORD")
COUCHDB_URL = "http://couchdb:5984"
COUCHDB_CORS_ORIGINS = os.getenv(
    "COUCHDB_CORS_ORIGINS"
)  # a string of origins separated by commas, e.g: "http://dev.example.com, http://dev.example.com:5984, http://dev.example.com:4200, http://dev.example.com:3000, http://dev.example.com:8080, https://stag.example.com, https://db.stag.example.com, https://example.com, https://db.example.com"
COUCHDB_AUTH_TIMEOUT = ACCESS_TOKEN_EXPIRE_MINUTES * 60

ROLE_ACTIVE = "active"
ROLE_SUPERUSER = "superuser"

FIRST_SUPERUSER = os.getenv("FIRST_SUPERUSER")
FIRST_SUPERUSER_PASSWORD = os.getenv("FIRST_SUPERUSER_PASSWORD")

USERS_OPEN_REGISTRATION = getenv_boolean("USERS_OPEN_REGISTRATION")
