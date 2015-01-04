#!/bin/bash

set +e

WORKING_DIR=`pwd`

sudo docker build -t nest-api .

sudo docker rm -f nest-api

sudo docker run -d \
    -p 5000:5000 \
    -v $WORKING_DIR:/nest-api \
    --name nest-api
    nest-api
