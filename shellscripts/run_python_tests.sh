#!/usr/bin/env bash

# Get repo path
CURRENT_DIR=${PWD}
SHELLSCRIPTS_DIR=$( cd "$(dirname "${BASH_SOURCE[0]}")" ; pwd -P )
REPO_DIR="${SHELLSCRIPTS_DIR}/.."
echo "Repository located at ${REPO_DIR}"

# LaneLineDetector
echo "Running LaneLineDetector test..."
python ${REPO_DIR}/python/scripts/algo/lane_detection/run_lane_detection.py \
    --image-path ${REPO_DIR}/data/kitti_data_road/testing/image_2/um_000000.png \
    --calib-path ${REPO_DIR}/data/kitti_data_road/testing/calib/um_000000.txt \
    --config-path ${REPO_DIR}/config/algo/lane_line_detector_config.json

echo "Done! Changing back to ${CURRENT_DIR}"
cd $CURRENT_DIR
