#!/bin/bash

set -e

git reset --hard origin/main
git pull origin main

sudo chmod 666 /var/run/docker.sock
docker-compose build
docker-compose down --rm all || true
