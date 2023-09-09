FROM ubuntu:latest

RUN apt update && \
    apt install -y git wget htop osmium-tool python3 python3-pip openjdk-8-jre-headless \
    libpostgis-java libpostgresql-jdbc-java \
    libpostgresql-jdbc-java libpostgis-java
RUN pip3 install osmium

WORKDIR /
RUN git clone https://github.com/stevo01/pyrenderer.git
WORKDIR /pyrenderer

VOLUME /data
