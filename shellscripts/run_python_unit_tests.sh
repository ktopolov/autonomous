#!/usr/bin/env bash

# Get repo path
CURRENT_DIR=${PWD}
SHELLSCRIPTS_DIR=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
REPO_DIR="${SHELLSCRIPTS_DIR}/.."
echo "Repository located at ${REPO_DIR}"

# Run pytest on all modules with coverage report
pytest \
    --cov-report term-missing \
    --cov=${REPO_DIR}/python/modules \
    ${REPO_DIR}/python/unittests
