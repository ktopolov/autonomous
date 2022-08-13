#!/bin/bash
# Script to push a Docker image to remote DockeHub repository
IMAGE_NAME_TAG="ktopolovec/autonomous:latest"

# Script to push a Docker image to remote DockeHub repository
if [ "$1" == "-h" ]; then
    echo "* Push docker image: source docker_push.sh \n"
    exit 0
fi

# If image not built, then exit
if ! test ! -z "$(docker images -q ${IMAGE_NAME_TAG})"; then
    echo -e "=== FAILED PUSH === \
          Docker image does not exist locally. Must either: \
          \n* Build image: source docker_build.sh \
          \n* Pull image: source docker_pull.sh"
    return
fi

# Must login if not already; if already, it'll automatically verify your credentials
echo "Logging into DockerHub..."
docker login

# Push image to remote repo
echo "Pushing docker image ${IMAGE_NAME_TAG} ..."
docker push ${IMAGE_NAME_TAG}

echo "Done pushing"
