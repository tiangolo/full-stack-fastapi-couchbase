from app import crud
from app.db.database import get_default_bucket
from app.models.config import ITEM_DOC_TYPE
from app.models.item import ItemCreate, ItemUpdate
from app.tests.utils.user import create_random_user
from app.tests.utils.utils import random_lower_string


def test_create_item():
    title = random_lower_string()
    description = random_lower_string()
    id = crud.utils.generate_new_id()
    item_in = ItemCreate(title=title, description=description)
    bucket = get_default_bucket()
    user = create_random_user()
    item = crud.item.upsert(
        bucket=bucket, id=id, doc_in=item_in, owner_username=user.username, persist_to=1
    )
    assert item.id == id
    assert item.type == ITEM_DOC_TYPE
    assert item.title == title
    assert item.description == description
    assert item.owner_username == user.username


def test_get_item():
    title = random_lower_string()
    description = random_lower_string()
    id = crud.utils.generate_new_id()
    item_in = ItemCreate(title=title, description=description)
    bucket = get_default_bucket()
    user = create_random_user()
    item = crud.item.upsert(
        bucket=bucket, id=id, doc_in=item_in, owner_username=user.username, persist_to=1
    )
    stored_item = crud.item.get(bucket=bucket, id=id)
    assert item.id == stored_item.id
    assert item.title == stored_item.title
    assert item.description == stored_item.description
    assert item.owner_username == stored_item.owner_username


def test_update_item():
    title = random_lower_string()
    description = random_lower_string()
    id = crud.utils.generate_new_id()
    item_in = ItemCreate(title=title, description=description)
    bucket = get_default_bucket()
    user = create_random_user()
    item = crud.item.upsert(
        bucket=bucket, id=id, doc_in=item_in, owner_username=user.username, persist_to=1
    )
    description2 = random_lower_string()
    item_update = ItemUpdate(description=description2)
    item2 = crud.item.update(
        bucket=bucket,
        id=id,
        doc_in=item_update,
        owner_username=item.owner_username,
        persist_to=1,
    )
    assert item.id == item2.id
    assert item.title == item2.title
    assert item.description == description
    assert item2.description == description2
    assert item.owner_username == item2.owner_username


def test_delete_item():
    title = random_lower_string()
    description = random_lower_string()
    id = crud.utils.generate_new_id()
    item_in = ItemCreate(title=title, description=description)
    bucket = get_default_bucket()
    user = create_random_user()
    item = crud.item.upsert(
        bucket=bucket, id=id, doc_in=item_in, owner_username=user.username, persist_to=1
    )
    item2 = crud.item.remove(bucket=bucket, id=id, persist_to=1)
    item3 = crud.item.get(bucket=bucket, id=id)
    assert item3 is None
    assert item2.id == id
    assert item2.title == title
    assert item2.description == description
    assert item2.owner_username == user.username
