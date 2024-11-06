#!/bin/bash

sudo chmod 666 /var/run/docker.sock

docker stop $(docker ps -aq) || true
docker rm $(docker ps -aq) || true
docker rmi $(docker images -q) || true
docker container prune -f || true
docker image prune -a -f || true
docker volume prune -f || true
docker network prune -f || true
docker builder prune -f || true
