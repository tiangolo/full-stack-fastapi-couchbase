from app.db.utils import (
    get_user_id,
    get_database_id_for_user,
)


def test_get_user_id():
    username = "johndoe@example.com"
    user_id = get_user_id(username)
    assert user_id == "org.couchdb.user:johndoe@example.com"


def test_get_database_id_for_user():
    username = "johndoe@example.com"
    database_id = get_database_id_for_user(username)
    assert database_id == "userdb-6a6f686e646f65406578616d706c652e636f6d"
