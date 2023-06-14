#!/bin/bash

set -o errexit
set -o pipefail
set -o nounset

if [ "$USE_GUNICORN" = "True" ]; then
    echo "Starting with GUNICORN"
    gunicorn src.$CD_APP_NAME --workers $CD_WORKERS --worker-class uvicorn.workers.UvicornWorker --bind $CD_HOST:$CD_PORT
else
    echo "Starting without GUNICORN"
    python src/main.py
fi
