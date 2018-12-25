import uuid
from enum import Enum
from typing import List, Sequence, Type, Union

from couchbase.bucket import Bucket
from couchbase.fulltext import QueryStringQuery
from couchbase.n1ql import CONSISTENCY_REQUEST, N1QLQuery
from pydantic import BaseModel

from app.core.config import COUCHBASE_BUCKET_NAME


def generate_new_id():
    return str(uuid.uuid4())


def ensure_enums_to_strs(items: Union[Sequence[Union[Enum, str]], Type[Enum]]):
    str_items = []
    for item in items:
        if isinstance(item, Enum):
            str_items.append(str(item.value))
        else:
            str_items.append(str(item))
    return str_items


def get_all_documents_by_type(bucket: Bucket, *, doc_type: str, skip=0, limit=100):
    query_str = f"SELECT *, META().id as id FROM {COUCHBASE_BUCKET_NAME} WHERE type = $type LIMIT $limit OFFSET $skip;"
    q = N1QLQuery(
        query_str, bucket=COUCHBASE_BUCKET_NAME, type=doc_type, limit=limit, skip=skip
    )
    q.consistency = CONSISTENCY_REQUEST
    result = bucket.n1ql_query(q)
    return result


def get_documents_by_keys(bucket: Bucket, *, keys: List[str], skip=0, limit=100):
    query_str = f"SELECT *, META().id as id FROM {COUCHBASE_BUCKET_NAME} USE KEYS $keys LIMIT $limit OFFSET $skip;"
    q = N1QLQuery(
        query_str, bucket=COUCHBASE_BUCKET_NAME, keys=keys, limit=limit, skip=skip
    )
    q.consistency = CONSISTENCY_REQUEST
    result = bucket.n1ql_query(q)
    return result


def results_to_model(results_from_couchbase: list, *, doc_model: Type[BaseModel]):
    items = []
    for doc in results_from_couchbase:
        data = doc[COUCHBASE_BUCKET_NAME]
        doc = doc_model(**data)
        items.append(doc)
    return items


def search_results_to_model(results_from_couchbase: list, *, doc_model: Type[BaseModel]):
    items = []
    for doc in results_from_couchbase:
        data = doc["fields"]
        doc = doc_model(**data)
        items.append(doc)
    return items


def get_docs(
    bucket: Bucket, *, doc_type: str, doc_model=Type[BaseModel], skip=0, limit=100
):
    doc_results = get_all_documents_by_type(
        bucket, doc_type=doc_type, skip=skip, limit=limit
    )
    return results_to_model(doc_results, doc_model=doc_model)


def get_doc(bucket: Bucket, *, doc_id: str, doc_model: Type[BaseModel]):
    result = bucket.get(doc_id, quiet=True)
    if not result.value:
        return None
    model = doc_model(**result.value)
    return model


def search_docs_get_doc_ids(
    bucket: Bucket,
    *,
    query_string: str,
    index_name: str,
    skip: int = 0,
    limit: int = 100,
):
    query = QueryStringQuery(query_string)
    hits = bucket.search(index_name, query, skip=skip, limit=limit)
    doc_ids = []
    for hit in hits:
        doc_ids.append(hit["id"])
    return doc_ids


def search_get_results(
    bucket: Bucket,
    *,
    query_string: str,
    index_name: str,
    skip: int = 0,
    limit: int = 100,
):
    query = QueryStringQuery(query_string)
    hits = bucket.search(index_name, query, fields=["*"], skip=skip, limit=limit)
    docs = []
    for hit in hits:
        docs.append(hit)
    return docs


def search_docs(
    bucket: Bucket,
    *,
    query_string: str,
    index_name: str,
    doc_model: Type[BaseModel],
    skip=0,
    limit=100,
):
    keys = search_docs_get_doc_ids(
        bucket=bucket,
        query_string=query_string,
        index_name=index_name,
        skip=skip,
        limit=limit,
    )
    doc_results = get_documents_by_keys(
        bucket=bucket, keys=keys, skip=skip, limit=limit
    )
    return results_to_model(doc_results, doc_model=doc_model)


def search_results(
    bucket: Bucket,
    *,
    query_string: str,
    index_name: str,
    doc_model: Type[BaseModel],
    skip=0,
    limit=100,
):
    doc_results = search_get_results(
        bucket=bucket,
        query_string=query_string,
        index_name=index_name,
        skip=skip,
        limit=limit,
    )
    return search_results_to_model(doc_results, doc_model=doc_model)
