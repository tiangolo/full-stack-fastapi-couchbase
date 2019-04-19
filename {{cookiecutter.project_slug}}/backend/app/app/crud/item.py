from couchbase.bucket import Bucket
from couchbase.n1ql import CONSISTENCY_REQUEST, N1QLQuery

from app.core import config
from app.models.config import ITEM_DOC_TYPE
from app.models.item import ItemCreate, ItemInDB, ItemUpdate

from . import utils

# Same as file name /app/app/search_index_definitions/items.json
full_text_index_name = "items"


def get_doc_id(id: str):
    return f"{ITEM_DOC_TYPE}::{id}"


def get(bucket: Bucket, *, id: str):
    doc_id = get_doc_id(id)
    return utils.get_doc(bucket=bucket, doc_id=doc_id, doc_model=ItemInDB)


def upsert(
    bucket: Bucket,
    *,
    id: str,
    doc_in: ItemCreate,
    owner_username: str,
    persist_to=0,
    ttl=0,
):
    doc_id = get_doc_id(id)
    doc = ItemInDB(**doc_in.dict(), id=id, owner_username=owner_username)
    return utils.upsert(
        bucket=bucket, doc_id=doc_id, doc_in=doc, persist_to=persist_to, ttl=ttl
    )


def update(
    bucket: Bucket,
    *,
    id: str,
    doc_in: ItemUpdate,
    owner_username=None,
    persist_to=0,
    ttl=0,
):
    doc_id = get_doc_id(id=id)
    doc = get(bucket, id=id)
    doc = doc.copy(update=doc_in.dict(skip_defaults=True))
    if owner_username is not None:
        doc.owner_username = owner_username
    return utils.upsert(
        bucket=bucket, doc_id=doc_id, doc_in=doc, persist_to=persist_to, ttl=ttl
    )


def remove(bucket: Bucket, *, id: str, persist_to=0):
    doc_id = get_doc_id(id)
    return utils.remove(
        bucket=bucket, doc_id=doc_id, doc_model=ItemInDB, persist_to=persist_to
    )


def get_multi(bucket: Bucket, *, skip=0, limit=100):
    return utils.get_docs(
        bucket=bucket,
        doc_type=ITEM_DOC_TYPE,
        doc_model=ItemInDB,
        skip=skip,
        limit=limit,
    )


def get_multi_by_owner(bucket: Bucket, *, owner_username: str, skip=0, limit=100):
    query_str = f"SELECT *, META().id as doc_id FROM {config.COUCHBASE_BUCKET_NAME} WHERE type = $type AND owner_username = $owner_username LIMIT $limit OFFSET $skip;"
    q = N1QLQuery(
        query_str,
        bucket=config.COUCHBASE_BUCKET_NAME,
        type=ITEM_DOC_TYPE,
        owner_username=owner_username,
        limit=limit,
        skip=skip,
    )
    q.consistency = CONSISTENCY_REQUEST
    doc_results = bucket.n1ql_query(q)
    return utils.doc_results_to_model(doc_results, doc_model=ItemInDB)


def search(bucket: Bucket, *, query_string: str, skip=0, limit=100):
    docs = utils.search_get_docs(
        bucket=bucket,
        query_string=query_string,
        index_name=full_text_index_name,
        doc_model=ItemInDB,
        skip=skip,
        limit=limit,
    )
    return docs


def search_with_owner(
    bucket: Bucket, *query_string: str, username: str, skip=0, limit=100
):
    username_filter = f"owner_username:{username}"
    if username_filter not in query_string:
        query_string = f"{query_string} {username_filter}"
    docs = utils.search_get_docs(
        bucket=bucket,
        query_string=query_string,
        index_name=full_text_index_name,
        doc_model=ItemInDB,
        skip=skip,
        limit=limit,
    )
    return docs


def search_get_search_results_to_docs(
    bucket: Bucket, *, query_string: str, skip=0, limit=100
):
    docs = utils.search_by_type_get_results_to_docs(
        bucket=bucket,
        query_string=query_string,
        index_name=full_text_index_name,
        doc_type=ITEM_DOC_TYPE,
        doc_model=ItemInDB,
        skip=skip,
        limit=limit,
    )
    return docs
