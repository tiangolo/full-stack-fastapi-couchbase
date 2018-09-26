# Import standard library packages

# Import installed packages
from raven.contrib.flask import Sentry

# Import app code
from app.main import app
from app.db.init_db import init_db
from app.core import config

# Set up CORS
from . import cors  # noqa

from .jwt import jwt  # noqa
from . import errors  # noqa

from ..api.api_v1 import api as api_v1  # noqa

app.config["SECRET_KEY"] = config.SECRET_KEY
app.config["SERVER_NAME"] = config.SERVER_NAME

sentry = Sentry(app, dsn=config.SENTRY_DSN)
