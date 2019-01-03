#!/bin/bash

echo "JWT_SECRET=$PROD_JWT_SECRET" > .env
echo "PORT=80" > .env
docker build -t nickpearson/comicgame .
echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin
docker push nickpearson/comicgame:latest
