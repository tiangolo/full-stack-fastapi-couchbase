from enum import Enum
from typing import Sequence, Type, Union

from app.core.config import COUCHBASE_BUCKET_NAME
from couchbase.bucket import Bucket
from couchbase.n1ql import CONSISTENCY_REQUEST, N1QLQuery


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
    result = bucket.n1ql_query(q)  # type: N1QLRequest
    return result
