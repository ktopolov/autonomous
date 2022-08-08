#!/bin/bash

# Get repo path
CURRENT_DIR=${PWD}
SHELLSCRIPTS_DIR=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
REPO_DIR="${SHELLSCRIPTS_DIR}/.."
echo "Repository located at ${REPO_DIR}"

cd REPO_DIR

# === Run Python Pipeline ===
echo "Python testing..."

source SHELLSCRIPTS_DIR/run_python_linting.sh
source SHELLSCRIPTS_DIR/run_python_unit_tests.sh
source SHELLSCRIPTS_DIR/run_python_tests.sh

# === Run C++ Pipeline ===
echo "C++ testing..."
cd ${REPO_DIR}/c++

# 1) Build code
cmake -S ./c++ -B ./c++/build
cmake --build ./c++/build

# 2) Run tests

# 3) Run apps
./c++/build/helloworld

# === Build and Run Docker Container
echo "Docker testing..."
docker build --tag "ktopolovec/autonomous" --file ./docker/Dockerfile .

# Restore directory to initial dir
cd ${CURRENT_DIR}
