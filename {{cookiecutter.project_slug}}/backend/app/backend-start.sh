#! /usr/bin/env bash

set -e

# Let the DB start
python /app/app/backend_pre_start.py


LOG_LEVEL=info
# Uncomment to squeeze performance in exchange of logs
# LOG_LEVEL=warning

CORES=$(nproc --all)
WORKERS_PER_CORE=${WORKERS_PER_CORE:-2}
DEFAULT_WEB_CONCURRENCY=$(($CORES * $WORKERS_PER_CORE))
export WEB_CONCURRENCY=${WEB_CONCURRENCY:-$DEFAULT_WEB_CONCURRENCY}
echo "Using these many workers: $WEB_CONCURRENCY"

gunicorn -k uvicorn.workers.UvicornWorker --log-level $LOG_LEVEL app.main:app --bind 0.0.0.0:80
