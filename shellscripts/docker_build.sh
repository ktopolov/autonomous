#!/bin/bash

# Script to build a Docker image locally
if [ "$1" == "-h" ]; then
  echo "* Build docker image: source docker_build.sh"
  echo "* Build docker image with no cache (from scratch): source docker_build.sh --no-cache"
  echo ""
  exit 0
fi

# Get repo path
SHELLSCRIPTS_DIR=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
REPO_DIR="${SHELLSCRIPTS_DIR}/.."
echo "Repository located at ${REPO_DIR}"

# Assume this script sits inside autonomous/shellscripts and that autonomous/docker/ folder contains
# Dockerfile
TAG="ktopolovec/autonomous:latest"
DOCKER_DIR=${REPO_DIR}/docker

if [ $1 == "--no-cache" ]; then
    # Sometimes for some reason Docker cache will be outdated and cause some apt install to fail.
    # using --no-cache resets completely, taking more time but giving a clean build
    echo "Building Docker image with tag ${TAG} : no cache used ..."
    docker build --file ${DOCKER_DIR}/Dockerfile-dev --tag "${TAG}" --no-cache ${REPO_DIR}
else
    echo "Building Docker image with tag ${TAG} ..."
    docker build --file ${DOCKER_DIR}/Dockerfile-dev --tag "${TAG}" ${REPO_DIR}
fi

echo "Done building"
