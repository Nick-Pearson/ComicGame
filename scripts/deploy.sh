#!/bin/bash

docker build -t nickpearson/comicgame .
echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin
docker push nickpearson/comicgame:latest
