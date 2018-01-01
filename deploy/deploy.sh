#!/usr/bin/env bash

eval "$(docker-machine env soundalike)"
docker-machine ssh soundalike sysctl -w vm.max_map_count=262144
echo "building"
docker-compose build
echo "starting up"
docker-compose up