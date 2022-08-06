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

# Local Imports
from modules.algo import lane_detection
from modules.data import kitti

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--data-path", type=str, required=True, help="Path to KITTI road data folder"
    )
    data_road_path = pathlib.Path("/mnt/c/Users/ktopo/Desktop/kitti/data_road")
    data_type = "training"
    frame_num = 20
    image, calib = kitti.read_kitti_road_data(
        data_road_path=data_road_path, data_type=data_type, frame_num=frame_num
    )
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
    plt.show()
