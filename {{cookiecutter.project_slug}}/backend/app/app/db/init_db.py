from app.core import config

from app.db.utils import create_or_get_user, create_user_with_default_db
from app.db.roles import add_user_to_db_admins, add_user_to_db_members

from app.db.database import (
    get_client,
    get_db_app,
    get_db_users,
    enable_cors,
    setup_cookie,
)


def init_db():
    # Secure main DB access by adding a single dummy user 'app'
    client = get_client()
    db_app = get_db_app(client)
    add_user_to_db_admins("app", db_app)
    add_user_to_db_members("app", db_app)
    # Create first superuser
    db_users = get_db_users(client)
    create_or_get_user(
        config.FIRST_SUPERUSER,
        config.FIRST_SUPERUSER_PASSWORD,
        is_superuser=True,
        db_users=db_users,
        client=client,
    )
    create_user_with_default_db(config.FIRST_SUPERUSER, config.FIRST_SUPERUSER_PASSWORD)
    db_app.create_query_index(fields=["type", "username"])
    db_users.create_query_index(fields=["type"])
    enable_cors()
    setup_cookie()
    # enable_couch_peruser()
