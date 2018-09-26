from cloudant.client import CouchDB
from cloudant.database import CouchDatabase
from app.couchdb_remote.database import RemoteCouchDatabase
from cloudant.error import CloudantDatabaseException, CloudantClientException


class RemoteCouchDB(CouchDB):
    """
    Encapsulates a remote CouchDB client, handling top level user API calls having to
    do with session and database management.

    Maintains a requests.Session for working with the instance specified in the
    constructor.

    By default, doesn't use the local cached data, but can be instantiated to do so.

    Parameters can be passed in to control behavior:

    :param str user: Username used to connect to CouchDB.
    :param str auth_token: Authentication token used to connect to CouchDB.
    :param bool admin_party: Setting to allow the use of Admin Party mode in
        CouchDB.  Defaults to ``False``.
    :param str url: URL for CouchDB server.
    :param str encoder: Optional json Encoder object used to encode
        documents for storage.  Defaults to json.JSONEncoder.
    :param requests.HTTPAdapter adapter: Optional adapter to use for
        configuring requests.
    :param bool connect: Keyword argument, if set to True performs the call to
        connect as part of client construction.  Default is False.
    :param bool auto_renew: Keyword argument, if set to True performs
        automatic renewal of expired session authentication settings.
        Default is False.
    :param float timeout: Timeout in seconds (use float for milliseconds, for
        example 0.1 for 100 ms) for connecting to and reading bytes from the
        server.  If a single value is provided it will be applied to both the
        connect and read timeouts.  To specify different values for each timeout
        use a tuple.  For example, a 10 second connect timeout and a 1 minute
        read timeout would be (10, 60).  This follows the same behaviour as the
        `Requests library timeout argument
        <http://docs.python-requests.org/en/master/user/quickstart/#timeouts>`_.
        but will apply to every request made using this client.
    :param bool use_basic_auth: Keyword argument, if set to True performs basic
        access authentication with server. Default is False.
    :param bool use_iam: Keyword argument, if set to True performs
        IAM authentication with server. Default is False.
        Use :func:`~cloudant.client.CouchDB.iam` to construct an IAM
        authenticated client.
    :param bool remote: If True, will not use the local cache and will always
        return fresh data from the database.
    """

    _DATABASE_CLASS = RemoteCouchDatabase

    def __init__(
        self,
        user,
        auth_token,
        admin_party=False,
        url=None,
        encoder=None,
        adapter=None,
        timeout=None,
        auto_renew=False,
        use_basic_auth=False,
        use_iam=False,
        connect=False,
        remote=True,
    ):
        super(RemoteCouchDB, self).__init__(
            user,
            auth_token,
            admin_party=admin_party,
            url=url,
            encoder=encoder,
            adapter=adapter,
            timeout=timeout,
            auto_renew=auto_renew,
            use_basic_auth=use_basic_auth,
            use_iam=use_iam,
            connect=connect,
        )
        self.remote = remote
        if (
            connect
            and self._DATABASE_CLASS == CouchDatabase
            or self._DATABASE_CLASS == RemoteCouchDatabase
        ):
            self.connect()

    def create_database(self, dbname, throw_on_exists=False, remote=None):
        if remote is None:
            remote = self.remote
        new_db = self._DATABASE_CLASS(self, dbname, remote=remote)
        try:
            new_db.create(throw_on_exists)
        except CloudantDatabaseException as ex:
            if ex.status_code == 412:
                raise CloudantClientException(412, dbname)
        super(RemoteCouchDB, self).__setitem__(dbname, new_db)
        return new_db

    def keys(self, remote=None):
        if remote is None:
            remote = self.remote
        if not remote:
            return list(super(RemoteCouchDB, self).keys(remote=False))
        return self.all_dbs()

    def __getitem__(self, key, remote=None):
        if remote is None:
            remote = self.remote
        if not remote:
            if key in list(self.keys(remote=False)):
                return super(CouchDB, self).__getitem__(key)
        db = self._DATABASE_CLASS(self, key, remote=remote)
        if db.exists():
            super(RemoteCouchDB, self).__setitem__(key, db)
            return db
        else:
            raise KeyError(key)

    def __delitem__(self, key, remote=None):
        if remote is None:
            remote = self.remote
        super(RemoteCouchDB, self).__delitem__(key, remote=remote)

    def __repr__(self):
        return super(RemoteCouchDB, self).__repr__()

    def get(self, key, default=None, remote=None):
        if remote is None:
            remote = self.remote
        return super(RemoteCouchDB, self).get(key, default, remote=remote)

    def __setitem__(self, key, value, remote=None):
        if remote is None:
            remote = self.remote
        super(RemoteCouchDB, self).__setitem__(key, value, remote=remote)
