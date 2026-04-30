#!/usr/bin/env bash
#
# stop-postgres.sh
# ================
# Stops the ephemeral PostgreSQL container started by start-postgres.sh and
# removes the generated .demo-postgres.env file.
# Because the container was started with --rm, stopping it also removes it.
#
# Usage:
#   ./stop-postgres.sh
#
# Requires: docker

set -euo pipefail

CONTAINER_NAME="python-db-postgres"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ENV_FILE="${SCRIPT_DIR}/.demo-postgres.env"

if ! docker info > /dev/null 2>&1; then
    echo "Error: Docker daemon is not running."
    exit 1
fi

if docker ps --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    echo "Stopping container '${CONTAINER_NAME}'…"
    docker stop "${CONTAINER_NAME}" > /dev/null
    echo "Stopped and removed."
else
    echo "Container '${CONTAINER_NAME}' is not running."
fi

if [[ -f "${ENV_FILE}" ]]; then
    rm -f "${ENV_FILE}"
    echo "Removed ${ENV_FILE}."
fi
