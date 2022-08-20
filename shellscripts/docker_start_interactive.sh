#!/bin/bash
# Script to pull a Docker image from remote DockeHub repository
IMAGE_NAME_TAG="ktopolovec/autonomous:latest"
docker run -it --entrypoint bash -v ${HOME}:${HOME} ${IMAGE_NAME_TAG}

# Set a bunch of helpful aliases
SHELLSCRIPTS_DIR=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
REPO_DIR="${SHELLSCRIPTS_DIR}/.."
