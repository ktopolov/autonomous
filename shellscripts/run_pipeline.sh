#!/usr/bin/env bash
CURRENT_DIR=${PWD}
SCRIPT_DIR=$(dirname "$SCRIPT")
REPO_DIR="${CURRENT_DIR}/${SCRIPT_DIR}"
echo "Repository located at ${REPO_DIR}"

# === Run Python Pipeline ===
echo "Python testing..."
cd ${REPO_DIR}/python

# 1) Lint code with Pylint
pylint --rc-file .pylintrc modules
pylint --rc-file .pylintrc scripts
pylint --rc-file .pylintrc tests

# 2) Run unit tests with pytest
pytest tests

# 3) Run Python scripts
python scripts/sample_script.py

# === Run C++ Pipeline ===
echo "C++ testing..."
cd ${REPO_DIR}/c++

# 1) Build code
cmake -S . -B ./build
cmake --build ./build

# 2) Run tests

# 3) Run apps
./build/helloworld

# === Build and Run Docker Container
echo "Docker testing..."
cd ${REPO_DIR}
docker build --tag mytag --file ./Dockerfile .

# Restore directory to initial dir
cd ${CURRENT_DIR}

