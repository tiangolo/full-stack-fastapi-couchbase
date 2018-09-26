from cloudant.database import CouchDatabase
from cloudant.design_document import DesignDocument
from cloudant.document import Document


class RemoteCouchDatabase(CouchDatabase):
    def __init__(self, client, database_name, fetch_limit=100, remote=True):
        super(RemoteCouchDatabase, self).__init__(
            client, database_name, fetch_limit
        )
        self.remote = remote

    def keys(self, remote=None):
        if remote is None:
            remote = self.remote
        return super(RemoteCouchDatabase, self).keys(remote=self.remote)

    def __getitem__(self, key):
        if not self.remote:
            if key in list(self.keys(remote=False)):
                return super(CouchDatabase, self).__getitem__(key)
        if key.startswith("_design/"):
            doc = DesignDocument(self, key)
        else:
            doc = Document(self, key)
        if doc.exists():
            doc.fetch()
            super(CouchDatabase, self).__setitem__(key, doc)
            return doc
        else:
            raise KeyError(key)

    def __contains__(self, key):
        if not self.remote:
            if key in list(self.keys(remote=False)):
                return True
        if key.startswith("_design/"):
            doc = DesignDocument(self, key)
        else:
            doc = Document(self, key)
        return doc.exists()

    def __iter__(self, remote=None):
        if remote is None:
            remote = self.remote
        super(RemoteCouchDatabase, self).__iter__(remote=remote)
        return
