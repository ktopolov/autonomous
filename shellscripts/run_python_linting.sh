#!/bin/bash

# Get repo path
CURRENT_DIR=${PWD}
SHELLSCRIPTS_DIR=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
REPO_DIR="${SHELLSCRIPTS_DIR}/.."
echo "Repository located at ${REPO_DIR}"

# 0) Auto-Format Python Code
black ${REPO_DIR}/python

# 1) Lint code with Pylint
pylint --rc-file ${REPO_DIR}/python/.pylintrc ${REPO_DIR}/python/modules
pylint --rc-file ${REPO_DIR}/python/.pylintrc ${REPO_DIR}/python/scripts
pylint --rc-file ${REPO_DIR}/python/.pylintrc ${REPO_DIR}/python/tests
