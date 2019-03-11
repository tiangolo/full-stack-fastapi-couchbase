from app import crud


def test_get_user_id():
    username = "johndoe@example.com"
    user_id = crud.user.get_doc_id(username)
    assert user_id == "userprofile::johndoe@example.com"
