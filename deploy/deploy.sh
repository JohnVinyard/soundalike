#!/usr/bin/env bash

eval "$(docker-machine env soundalike)"
echo "building"
docker-compose --verbose build --force-rm
echo "starting up"
docker-compose --verbose up