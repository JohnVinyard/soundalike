#!/usr/bin/env bash

eval "$(docker-machine env soundalike)"
echo "building"
docker-compose build
echo "starting up"
docker-compose up