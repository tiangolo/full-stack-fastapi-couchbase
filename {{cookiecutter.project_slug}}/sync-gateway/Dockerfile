FROM couchbase/sync-gateway:2.1.0-community
RUN yum install -y dos2unix

COPY /entrypoint.sh /
RUN dos2unix /entrypoint.sh
RUN chmod +x ./entrypoint.sh

COPY /create_config.py /
COPY /sync/ /sync/
