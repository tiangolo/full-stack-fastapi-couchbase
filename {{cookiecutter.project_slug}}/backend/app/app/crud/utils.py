from couchbase.bucket import Bucket
from couchbase.n1ql import N1QLQuery, N1QLRequest

from app.core.config import COUCHBASE_BUCKET_NAME

from typing import Sequence, Union
from enum import Enum


def ensure_enums_to_strs(items: Sequence[Union[Enum, str]]):
    str_items = []
    for item in items:
        if isinstance(item, Enum):
            str_items.append(str(item.value))
        else:
            str_items.append(str(item))
    return str_items


def get_all_documents_by_type(bucket: Bucket, *, doc_type: str, skip=0, limit=100):
    query_str = f"SELECT *, META().id as id FROM {COUCHBASE_BUCKET_NAME} WHERE type = $type LIMIT $limit OFFSET $skip;"
    doc_type = "userprofile"
    q = N1QLQuery(
        query_str, bucket=COUCHBASE_BUCKET_NAME, type=doc_type, limit=limit, skip=skip
    )
    result = bucket.n1ql_query(q)  # type: N1QLRequest
    return result
