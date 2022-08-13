#!/bin/bash
# Script to pull a Docker image from remote DockeHub repository
IMAGE_NAME_TAG="ktopolovec/autonomous:latest"
docker run -it --entrypoint bash ${IMAGE_NAME_TAG} -v:${HOME}:${HOME}
