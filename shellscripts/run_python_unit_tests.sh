#!/usr/bin/env bash

# Get repo path
CURRENT_DIR=${PWD}
SCRIPT_DIR=$(dirname "$SCRIPT")
REPO_DIR="${CURRENT_DIR}/${SCRIPT_DIR}"
echo "Repository located at ${REPO_DIR}"

# Run pytest on all modules with coverage report
pytest --cov-report term-missing --cov=${REPO_DIR}/python/modules ${REPO_DIR}/python/tests
