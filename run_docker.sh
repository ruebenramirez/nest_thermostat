#!/bin/bash

set +e
WORKING_DIR=`pwd`
sudo docker rmi nest-api
sudo docker build -t nest-api .
sudo docker pull redis
sudo docker rm -f nest-api redis-host

sudo docker run -d \
    --name redis-host \
    redis

sudo docker run -d \
    -p 80:5000 \
    -v $WORKING_DIR:/nest-api \
    --link redis-host:redis-host \
    --name nest-api \
    nest-api

sudo docker logs -f nest-api
