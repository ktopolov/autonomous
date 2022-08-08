"""Script to run lane detection algorithm on a loaded image

To use this:
1) Go to http://www.cvlibs.net/datasets/kitti/eval_road.php
2) Select the "Download base kit with: left color images, calibration and training labels (0.5 GB)"
3) Unzip contents into data_road/ folder
"""
# Standard Imports
import pathlib
import json
import argparse

# Third Party Imports
import matplotlib.pyplot as plt
import cv2
import numpy as np

# Local Imports
from modules.algo import lane_detection
from modules.data import kitti
from modules.common import computer_vision as cvision


def parse_cli_args() -> argparse.Namespace:
    """Parse command line arguments

    Returns:
        cli_args: Command line arguments accessible via cli_args.name
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--image-path", type=str, required=True, help="Path to .png road image"
    )
    parser.add_argument(
        "--calib-path", type=str, required=True, help="Path to calibration .txt file"
    )
    parser.add_argument(
        "--config-path",
        type=str,
        required=True,
        help="Path to configuration .json file for LaneLineDetector",
    )
    parser.add_argument(
        "--show-plots",
        action="store_true",  # default false
        default=False,
        help="Whether to show plots and halt execution",
    )
    cli_args = parser.parse_args()
    return cli_args


if __name__ == "__main__":
    args = parse_cli_args()

    image = cv2.imread(args.image_path)
    assert image is not None, "Image could not be read; may not exist"

    # Load calibration
    calib_path = pathlib.Path(args.calib_path)
    assert calib_path.is_file(), f"Calibration file {calib_path} does not exist"
    calib = kitti.read_calib_to_dict(path=calib_path)

    config_path = pathlib.Path(args.config_path)
    config = None
    with open(config_path) as json_file:
        config = json.load(json_file)

    camera_matrix = calib["P2:"][:3, :3]
    LaneDetector = lane_detection.LaneLineDetector(
        config=config,
        tr_cam_to_road=calib["Tr_cam_to_road:"],
        camera_matrix=camera_matrix,
    )

    out = LaneDetector.run(
        image=image,
        fig_num=1,
    )
    print("=== OUTPUTS ===")
    for key, value in out.items():
        print(f"{key}: {value}")

    if args.show_plots:
        plt.show()
