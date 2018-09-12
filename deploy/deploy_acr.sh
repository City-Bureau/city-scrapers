#!/bin/bash

docker login -u $DOCKER_USER -p $DOCKER_PASSWORD $CONTAINER_REGISTRY
docker build --pull -f deploy/Dockerfile -t $CONTAINER_REGISTRY/$IMAGE_NAME:latest .
docker push $CONTAINER_REGISTRY/$IMAGE_NAME:latest
