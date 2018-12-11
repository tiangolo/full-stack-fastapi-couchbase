#! /usr/bin/env bash

# Let the DB start
python /app/app/backend_pre_start.py

gunicorn -w 4 -k uvicorn.workers.UvicornWorker --log-level warning app.main:app --bind 0.0.0.0:80
