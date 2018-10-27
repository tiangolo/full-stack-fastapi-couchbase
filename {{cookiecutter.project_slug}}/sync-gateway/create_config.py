from __future__ import print_function
import os
import json
import logging

logging.basicConfig(level=logging.INFO)


def getenv_boolean(var_name, default_value=False):
    result = default_value
    env_value = os.getenv(var_name)
    if env_value is not None:
        result = env_value.upper() in ("TRUE", "1")
    return result


# Env vars for configs
COUCHBASE_HOST = os.getenv(
    "COUCHBASE_HOST", ""
)  # e.g.: "couchbase". Leave empty to use default Walrus
COUCHBASE_PORT = os.getenv("COUCHBASE_PORT", "8091")
COUCHBASE_BUCKET_NAME = os.getenv("COUCHBASE_BUCKET_NAME", "app")
COUCHBASE_SYNC_GATEWAY_LOG = os.getenv(
    "COUCHBASE_SYNC_GATEWAY_LOG", "HTTP+"
)  # e.g.: "*"
COUCHBASE_SYNC_GATEWAY_ADMIN_INTERFACE = os.getenv(
    "COUCHBASE_SYNC_GATEWAY_ADMIN_INTERFACE", ""
)  # e.g.: ":4985", leave empty to disable
COUCHBASE_SYNC_GATEWAY_USER = os.getenv("COUCHBASE_SYNC_GATEWAY_USER", "")
COUCHBASE_SYNC_GATEWAY_PASSWORD = os.getenv("COUCHBASE_SYNC_GATEWAY_PASSWORD", "")
COUCHBASE_SYNC_GATEWAY_DATABASE = os.getenv("COUCHBASE_SYNC_GATEWAY_DATABASE", "db")
COUCHBASE_SYNC_GATEWAY_CORS_ORIGINS = os.getenv(
    "COUCHBASE_SYNC_GATEWAY_CORS_ORIGINS", ""
)
COUCHBASE_SYNC_GATEWAY_USE_VIEWS = getenv_boolean(
    "COUCHBASE_SYNC_GATEWAY_USE_VIEWS", default_value=True
)
COUCHBASE_SYNC_GATEWAY_DISABLE_GUEST_USER = getenv_boolean(
    "COUCHBASE_SYNC_GATEWAY_DISABLE_GUEST_USER", default_value=False
)

# Base config
logging.info("Generating base config")
config_dict = {
    "interface": ":4984",
    "log": [COUCHBASE_SYNC_GATEWAY_LOG],
    "databases": {},
}

# Admin interface
logging.info("Checking adminInterface config config")
if COUCHBASE_SYNC_GATEWAY_ADMIN_INTERFACE:
    logging.info("Generating adminInterface config config")
    config_dict["adminInterface"] = COUCHBASE_SYNC_GATEWAY_ADMIN_INTERFACE

# CORS
logging.info("Checking CORS config")
if COUCHBASE_SYNC_GATEWAY_CORS_ORIGINS:
    cors_list = COUCHBASE_SYNC_GATEWAY_CORS_ORIGINS.split(",")
    use_cors = [origin.strip() for origin in cors_list]

    logging.info("Generating CORS config")
    config_dict["CORS"] = {
        "Origin": use_cors,
        "LoginOrigin": use_cors,
        "Headers": ["Content-Type"],
        "MaxAge": 17280000,
    }

# Couchbase
logging.info("Checking Couchbase config")
if COUCHBASE_HOST and COUCHBASE_SYNC_GATEWAY_USER and COUCHBASE_SYNC_GATEWAY_PASSWORD:
    logging.info("Generating Couchbase config")
    use_server = "http://{COUCHBASE_HOST}:{COUCHBASE_PORT}".format(
        COUCHBASE_HOST=COUCHBASE_HOST, COUCHBASE_PORT=COUCHBASE_PORT
    )

    config_dict["databases"][COUCHBASE_SYNC_GATEWAY_DATABASE] = {
        "server": use_server,
        "bucket": COUCHBASE_BUCKET_NAME,
        "username": COUCHBASE_SYNC_GATEWAY_USER,
        "password": COUCHBASE_SYNC_GATEWAY_PASSWORD,
        "use_views": COUCHBASE_SYNC_GATEWAY_USE_VIEWS,
        "enable_shared_bucket_access": True,
        "import_docs": "continuous",
        "users": {"GUEST": {"disabled": COUCHBASE_SYNC_GATEWAY_DISABLE_GUEST_USER}},
    }
else:
    config_dict["databases"][COUCHBASE_SYNC_GATEWAY_DATABASE] = {
        "server": "walrus:/opt/couchbase-sync-gateway/data",
        "users": {
            "GUEST": {
                "disabled": COUCHBASE_SYNC_GATEWAY_DISABLE_GUEST_USER,
                "admin_channels": ["*"],
            }
        },
    }

# JS sync function
logging.info("Checking JavaScript sync function file")
js_function_path = "/sync/sync-function.js"
sync_function = ""
logging.info("Checking JS sync function from {}".format(js_function_path))
if os.path.isfile(js_function_path):
    logging.info("Reading JavaScript sync function file")
    with open(js_function_path) as f:
        sync_function = f.read()
if sync_function:
    logging.info("Generating JavaScript sync function config")
    config_dict["databases"][COUCHBASE_SYNC_GATEWAY_DATABASE]["sync"] = sync_function

# Generate JSON config
logging.info("Writing final config JSON file")
with open("/etc/sync_gateway/config.json", "w") as f:
    json.dump(config_dict, f, indent=2)
logging.info("Done")
