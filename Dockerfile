FROM ubuntu:14.04

MAINTAINER Rueben Ramirez <ruebenramirez@gmail.com>

RUN mkdir /nest-api
RUN apt-get update -y
RUN apt-get upgrade -y
RUN apt-get install -y build-essential python python-dev python-pip

WORKDIR /nest-api
ADD requirements.txt /nest-api/requirements.txt
RUN pwd
RUN ls -lah
RUN pip install -r requirements.txt

VOLUME ["/nest-api"]
EXPOSE 5000
CMD ["python", "nest_api.py"]


