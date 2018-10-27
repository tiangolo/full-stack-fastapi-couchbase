FROM couchbase/sync-gateway:2.1.0-community

COPY /entrypoint.sh /
RUN chmod +x ./entrypoint.sh

COPY /create_config.py /
COPY /sync/ /sync/
