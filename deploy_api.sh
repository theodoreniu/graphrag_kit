#!/bin/bash

set -e

if [ -f .env ]; then
  source .env
fi

if [ -z "$APP_NAME" ]; then
  echo "APP_NAME is not set"
  exit 1
fi

export DOCKER_FILE="Dockerfile.api"

bash deploy.sh "${APP_NAME}-api"
