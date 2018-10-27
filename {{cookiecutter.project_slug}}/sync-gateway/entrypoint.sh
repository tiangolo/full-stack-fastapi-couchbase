#! /usr/bin/env bash

set -e

# Check connection in a separate function, that way, when 
# there's no connection available yet and the return of the command
# is non-zero, the script doesn't exit yet
check_connection() {
    curl -Is http://${COUCHBASE_SYNC_GATEWAY_USER}:${COUCHBASE_SYNC_GATEWAY_PASSWORD}@${COUCHBASE_HOST}:${COUCHBASE_PORT}/pools/default/buckets/${COUCHBASE_BUCKET_NAME} 2>&1 | grep "HTTP/1.1 200 OK" > /dev/null
    if [ $? -eq 0 ]; then
        echo "success";
    else
        echo "error";
    fi;
}

# Try to connect to Couchbase only if COUCHBASE_HOST was declared as an env var
if [ ! -z $COUCHBASE_HOST ]; then
    # Try once per second, up to 300 times (5 min)
    SECONDS_TO_TRY=300
    for i in $(seq 1 $SECONDS_TO_TRY); do
        echo "Checking connection, trial ${i}";
        result=$(check_connection);
        if [ $result == "success" ]; then
            echo "Success: connection checked";
            sleep 1;
            break;
        else
            echo "Connection not available yet, sleeping 1 sec...";
            sleep 1;
            echo "----------";
        fi;
    done;
fi;


python create_config.py

LOGFILE_DIR=/var/log/sync_gateway
mkdir -p $LOGFILE_DIR

LOGFILE_ACCESS=$LOGFILE_DIR/sync_gateway_access.log
LOGFILE_ERROR=$LOGFILE_DIR/sync_gateway_error.log

# Run SG and use tee to append stdout and stderr to separate logfiles
# Process substitution described here: https://stackoverflow.com/a/692407
exec sync_gateway "$@" > >(tee -a $LOGFILE_ACCESS) 2> >(tee -a $LOGFILE_ERROR >&2)
