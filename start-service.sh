#!/bin/bash
docker stop awslogin || true
docker rm awslogin || true
docker create --name awslogin --restart always \
    -p 127.0.0.1:1999:5000 \
    -v ~/.aws:/root/.aws \
    cheneyyan/awslogin
docker start awslogin