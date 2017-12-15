#!/usr/bin/env bash

eval "$(docker-machine env soundalike)"
echo "building"
docker-compose --verbose build
echo "starting up"
docker-compose --verbose up -d