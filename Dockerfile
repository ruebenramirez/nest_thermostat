FROM ubuntu:14.04

MAINTAINER Rueben Ramirez <ruebenramirez@gmail.com>

RUN mkdir /nest-api
RUN apt-get update -y && \
    apt-get upgrade -y && \
    apt-get install -y build-essential python python-dev python-pip python-virtualenv

WORKDIR /nest-api

ADD requirements.txt /nest-api/requirements.txt

RUN /bin/bash -c "virtualenv /opt/.venv && \
    source /opt/.venv/bin/activate && \
    pip install -r /nest-api/requirements.txt"

VOLUME ["/nest-api"]
EXPOSE 5000
CMD ["/nest-api/runflask-debug.sh"]


