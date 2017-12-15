#!/usr/bin/env bash

# https://developer.rackspace.com/blog/dev-to-deploy-with-docker-machine-and-compose/
#export OS_USERNAME=RACKSPACE_USERNAME
#export OS_API_KEY=RACKSPACE_API_KEY
#export OS_REGION_NAME=RACKSPACE_REGION_NAME

echo $OS_USERNAME
echo $OS_API_KEY
echo $OS_REGION_NAME

echo "creating machine"
docker-machine create \
    --driver rackspace --rackspace-flavor-id general1-2 \
    --engine-storage-driver overlay2 soundalike
echo "$(docker-machine ip soundalike)"

echo "securing machine"
docker-machine ssh soundalike "apt-get update"
docker-machine ssh soundalike "apt-get -y install fail2ban"
docker-machine ssh soundalike "ufw default deny"
docker-machine ssh soundalike "ufw allow ssh"
docker-machine ssh soundalike "ufw allow http"
docker-machine ssh soundalike "ufw allow 2376" # Docker
docker-machine ssh soundalike "ufw --force enable"