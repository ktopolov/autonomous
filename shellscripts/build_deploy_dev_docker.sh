#!/usr/bin/env bash

# Get repo path
CURRENT_DIR=${PWD}
SHELLSCRIPTS_DIR=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
REPO_DIR="${SHELLSCRIPTS_DIR}/.."
echo "Repository located at ${REPO_DIR}"

# Assume this script sits inside autonomous/shellscripts
# and that autonomous/docker/ folder contains dockerfile
DOCKER_DIR=${REPO_DIR}/docker

# 0) Log into Docker so that later we can push the build image. May prompt you
# for username/password
echo "Logging into DockerHub..."
docker login

# 1) Build container; must give context as ${REPO_DIR} so docker container has CWD as top of repo
#    and can copy all repo into docker container
TAG="ktopolovec/autonomous"
echo "Building Docker image with tag ${TAG}"
docker build --file ${DOCKER_DIR}/Dockerfile-dev --tag "${TAG}" ${REPO_DIR}

# 2) Push to remote repo with default tag "latest"
echo "Pushing docker image"
docker push ${TAG}

echo "DONE WITH EVERYTHING"
