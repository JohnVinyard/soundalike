#!/usr/bin/env bash

eval "$(docker-machine env soundalike)"
echo "building"
docker-compose build --force-rm
echo "starting up"
docker-compose up