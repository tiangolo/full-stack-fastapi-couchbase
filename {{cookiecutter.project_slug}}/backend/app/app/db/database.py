from couchbase.cluster import Cluster
from couchbase.cluster import PasswordAuthenticator
from couchbase.admin import Admin
from couchbase.exceptions import HTTPError
from app.db.couchbase_utils import get_cluster_couchbase_url
# Types
from couchbase.bucket import Bucket

def ensure_create_bucket(username: str, password: str, bucket_name: str, host="couchbase", port="8091"):
    adm = Admin(username, password, host=host, port=port)
    try:
        adm.bucket_create(bucket_name, bucket_type="couchbase")
        return True
    except HTTPError as e:
        if e.objextra.value["errors"]["name"] == 'Bucket with given name already exists':
            return True

def get_bucket(username:str, password: str, bucket_name: str, host="couchbase", port="8091"):
    # cluster_url="couchbase://couchbase"
    # username = "Administrator"
    # password = "password"
    cluster_url = get_cluster_couchbase_url(host=host, port=port)
    cluster = Cluster(cluster_url)
    authenticator = PasswordAuthenticator(username, password)
    cluster.authenticate(authenticator)
    bucket = cluster.open_bucket(bucket_name)
    return bucket

def ensure_create_primary_index(bucket: Bucket):
    manager = bucket.bucket_manager()
    return manager.n1ql_index_create_primary(ignore_exists=True)

def ensure_create_type_index(bucket: Bucket):
    manager = bucket.bucket_manager()
    return manager.n1ql_index_create("idx_type", ignore_exists=True, fields=["type"])
