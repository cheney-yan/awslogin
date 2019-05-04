#!/bin/bash
tag=$(git tag | grep -e '^v' | tail -1)
docker build -t cheneyyan/awslogin:$tag .
docker push cheneyyan/awslogin:$tag
docker tag cheneyyan/awslogin:$tag cheneyyan/awslogin:latest
docker push cheneyyan/awslogin:latest
