#!/bin/bash

docker login -u $DOCKER_USER -p $DOCKER_PASSWORD $CONTAINER_REGISTRY
docker --pull build -f deploy/Dockerfile -t $CONTAINER_REGISTRY/$IMAGE_NAME:latest
docker push $CONTAINER_REGISTRY/$IMAGE_NAME:latest
