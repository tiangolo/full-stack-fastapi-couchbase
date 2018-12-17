#! /usr/bin/env bash

set -e

# Let the DB start
python /app/app/backend_pre_start.py


LOG_LEVEL=info
# Uncomment to squeeze performance in exchange of logs
# LOG_LEVEL=warning

# Get CPU cores
CORES=$(nproc --all)
# Read env var WORKERS_PER_CORE with default of 2
WORKERS_PER_CORE=${WORKERS_PER_CORE:-2}
# Compute DEFAULT_WEB_CONCURRENCY as CPU cores * workers per core
DEFAULT_WEB_CONCURRENCY=$(($CORES * $WORKERS_PER_CORE))
# Read WEB_CONCURRENCY env var, with default of computed value
WEB_CONCURRENCY=${WEB_CONCURRENCY:-$DEFAULT_WEB_CONCURRENCY}
# Convert WEB_CONCURRENCY to int (if it was float)
WEB_CONCURRENCY=${WEB_CONCURRENCY%.*}
echo "Using these many workers: $WEB_CONCURRENCY"

gunicorn -k uvicorn.workers.UvicornWorker --log-level $LOG_LEVEL app.main:app --bind 0.0.0.0:80
