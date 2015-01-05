#!/bin/bash

set +e
WORKING_DIR=`pwd`
sudo docker rmi nest-api
sudo docker build -t nest-api .
sudo docker ps -a | grep nest-api | grep -v 'CONTAINER' | awk '{print $1}' | xargs sudo docker rm -f

sudo docker run -d \
    -p 5000:5000 \
    -v $WORKING_DIR:/nest-api \
    --name nest-api \
    nest-api

sudo docker logs -f nest-api
