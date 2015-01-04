FROM Ubuntu:14.04

MAINTAINER Rueben Ramirez <ruebenramirez@gmail.com>

RUN mkdir /nest-api
RUN apt-get update -y
RUN apt-get upgrade -y
RUN apt-get install build-essential python python-dev python-pip 

VOLUME ["/nest-api"]

EXPOSE 5000

WORKDIR /nest-api

CMD ["python", "nest_api.py"]


