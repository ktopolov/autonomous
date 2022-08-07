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

# Local Imports
from modules.algo import lane_detection
from modules.data import kitti


def parse_cli_args() -> argparse.Namespace:
    """Parse command line arguments

    Returns:
        cli_args: Command line arguments accessible via cli_args.name
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--image-path",
        type=str,
        required=True,
        help="Path to .png road image"
    )
    parser.add_argument(
        "--calib-path",
        type=str,
        required=True,
        help="Path to calibration .txt file"
    )
    parser.add_argument(
        "--config-path",
        type=str,
        required=True,
        help="Path to configuration .json file for LaneLineDetector",
    )
    parser.add_argument(
        "--show-plots",
        action='store_true',  # default false
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

    config_path = pathlib.Path(
        "/home/ktopolov/repos/autonomous/config/algo/lane_line_detector_config.json"
    )
    config = None
    with open(config_path) as json_file:
        config = json.load(json_file)
    LaneDetector = lane_detection.LaneLineDetector(config=config)

    LaneDetector.run(
        image=image, road_to_cam_proj_mat=calib["Tr_cam_to_road:"], fig_num=1
    )

    # TODO
    # 1) Transform all found lines to x/y ROAD COORDINATES (real world)
    # 2) Instead of checking left/right based on image slope, find one line, and omit any other line
    #    which is CLOSE to this one. left/right lane lines should be at least 1m appart roughly.
    # 3) update algorithm to output slope/intercept

    # Project into real-world (assume road coordinate frame +z is normal to road, x/y in road)
    # cam_to_road = calib['Tr_cam_to_road:']
    # camera_matrix, rotmat_to_cam, tvec_world_to_cam = cv2.decomposeProjectionMatrix(cam_to_road)[:3]
    # tvec_world_to_cam = tvec_world_to_cam[:3] / tvec_world_to_cam[3]  # from homogeneous to cartesian

    # cvision.apply_perspective_transform(
    #     v: np.ndarray,
    #     transform: np.ndarray
    # )

    # FIXME-KT: Decompose this into camera and extrinsic matrices, rotate points via homography into
    # road frame (augment pixels from 2D to 3D, apply 3D rotation homography, assign a depth and recover
    # 3D point using https://medium.com/yodayoda/from-depth-map-to-point-cloud-7473721d3f)
    #
    # Then, report line slope and intercept in real-world (or rho/theta?)
    if args.show_plots:
        plt.show()
