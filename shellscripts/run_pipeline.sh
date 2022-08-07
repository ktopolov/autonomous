#!/usr/bin/env bash
CURRENT_DIR=${PWD}
SHELLSCRIPTS_DIR=$(dirname "$SCRIPT")
REPO_DIR="${CURRENT_DIR}/${SHELLSCRIPTS_DIR}"
echo "Repository located at ${REPO_DIR}"

cd REPO_DIR

# === Run Python Pipeline ===
echo "Python testing..."

# 0) Auto-Format Python Code
black ./python

# 1) Lint code with Pylint
pylint --rc-file .pylintrc python/modules
pylint --rc-file .pylintrc python/scripts
pylint --rc-file .pylintrc python/tests

# 2) Run unit tests with pytest
pytest unittests

# 3) Run Python tests
python python/scripts/algo/lane_detection/run_lane_detection.py \
    --image-path ./data/kitti_data_road/testing/image_2/um_000000.png \
    --calib-path ./data/kitti_data_road/testing/calib/um_000000.txt \
    --config-path ./config/algo/lane_line_detector_config.json

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
docker build --tag mytag --file ./docker/Dockerfile .

# Restore directory to initial dir
cd ${CURRENT_DIR}
