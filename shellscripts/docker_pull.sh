#!/bin/bash
# Script to pull a Docker image from remote DockeHub repository
IMAGE_NAME_TAG="ktopolovec/autonomous:latest"

# Script to push a Docker image to remote DockeHub repository
if [ "$1" == "-h" ]; then
    echo "* Pull docker image: source docker_pull.sh \n"
    exit 0
fi

# Must login if not already; if already, it'll automatically verify your credentials
echo "Logging into DockerHub..."
docker login

# Push image to remote repo
echo "Pulling docker image ${IMAGE_NAME_TAG} ..."
docker pull ${IMAGE_NAME_TAG}

echo "Done pulling"
