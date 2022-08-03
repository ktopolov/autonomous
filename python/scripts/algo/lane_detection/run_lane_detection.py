"""Script to run lane detection algorithm on a loaded image

To use this:
1) Go to http://www.cvlibs.net/datasets/kitti/eval_road.php
2) Select the "Download base kit with: left color images, calibration and training labels (0.5 GB)"
3) Unzip contents into data_road/ folder
"""
# Standard Imports
import pathlib

# Third Party Imports
import cv2
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Local Imports
from modules.algo import lane_detection

def read_kitti_road_data(
    data_road_path: pathlib.Path,
    data_type: str = 'training',
    frame_num: int = 0
):
    """Read from the Kitti Road dataset found at http://www.cvlibs.net/datasets/kitti/eval_road.php

    See https://medium.com/test-ttile/kitti-3d-object-detection-dataset-d78a762b5a4 for help
    understanding the KITTI calibration information

    Args:
        data_road_path: Path to data_road/ folder (top-level of KITTI ROAD dataset)
        data_type: 'training' or 'testing'
        frame_num: Frame number

    Returns:
        image_2: Image from camera 2
        calib: Dictionary containing calibration information for all sensors
    """
    # Load image
    assert data_type in ['training', 'testing'], 'Unknown data type'
    image_path = data_road_path / f'{data_type}/image_2/um_{frame_num:06d}.png'
    image = cv2.imread(str(image_path))

    # Load calibration
    calib_path = data_road_path / f'{data_type}/calib/um_{frame_num:06d}.txt'
    calib_df = pd.read_csv(calib_path, delimiter=' ', header=None, index_col=0)

    calib = {
        index: np.array(calib_df.loc[index]).reshape((3, 4)) \
            for index in calib_df.index.values.tolist()
    }

    return image, calib

data_road_path = pathlib.Path('/mnt/c/Users/ktopo/Desktop/kitti/data_road')
data_type = 'training'
frame_num = 10
image, calib = read_kitti_road_data(
    data_road_path=data_road_path,
    data_type=data_type,
    frame_num=frame_num
)

class LaneLineDetector():
    """"Class to run lane detection algorithm"""
    def __init__(
        self,
        config: dict,
    ):
        """Initialize instance

        Args:
            config: Configuration parameters:
            road_to_cam_proj_mat: (3, 4) projection matrix from road to camera; composed of
                                  K * [R | t]
        """
        pass

    def run(
        self,
        image: np.ndarray,
        road_to_cam_proj_mat: np.ndarray,
        fig_num=None,
    ) -> dict:
        """Run algorithm for lane line detection

        Args:
            image : (n_row, n_col, 3) BGR image

        Returns:
            out: Contains output parameters
                'left_lane_slope': Slope of left lane line w.r.t. road coordinates
                'left_lane_intercept': Intercept of left lane line w.r.t. road coordinates
                'right_lane_slope': Slope of right lane line w.r.t. road coordinates
                'right_lane_intercept': Intercept of right lane line w.r.t. road coordinates
        """
        # Convert to HSV and select only the value channel
        image_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
        image_value = image_hsv[:, :, 2]

        # Apply Gaussian blur to image
        blur_kernel_shape = (5, 5)
        image_blur = cv2.GaussianBlur(image_value, blur_kernel_shape, 0)

        # Canny Edge Detection
        low_threshold = 130
        high_threshold = 200
        image_edges = cv2.Canny(
            image_blur,
            low_threshold,
            high_threshold,
            apertureSize=3
        )

        # Create Region of Interest Mask
        roi_polygon = [(398, 375), (493, 181), (1231, 357)]
        n_row, n_col, _ = image.shape
        roi_mask = np.zeros_like(image, shape=(n_row, n_col))
        cv2.fillPoly(roi_mask, np.array([roi_polygon]), 255)

        # Threshold for white lines only
        threshold = 200
        threshold_mask = image_value > threshold

        # Intersect edges with white threshold mask
        image_edges_with_mask = image_edges * threshold_mask * roi_mask

        # Detect lines in mask
        rho_res = 2  # pixels resolution
        theta_res = 2.0  # degrees
        accumulator_threshold = 10  # number of hits along line
        lines = cv2.HoughLinesP(
            image_edges_with_mask,
            rho_res,
            np.deg2rad(theta_res),
            threshold=accumulator_threshold,
            minLineLength=20,
            maxLineGap=10
        )

        # Store indices of msot confident left and right linea
        i_left_line = None
        i_right_line = None

        n_line = lines.shape[0]
        n_row, n_col, _ = image.shape
        for i_line in range(n_line):
            # Lines ordered by confidence level
            x1, y1, x2, y2 = lines[i_line, 0, :]
            slope = (y2 - y1) / (x2 - x1)
            intercept = y2 - slope * x2
            line_side = lane_detection.check_lane_side(
                slope=slope,
                intercept=intercept,
                n_row=n_row,
                n_col=n_col
            )

            if (line_side == 'left') and (i_left_line is None):
                i_left_line = i_line
            elif (line_side == 'right') and (i_right_line is None):
                i_right_line = i_line

            if (i_left_line is not None) and (i_right_line is not None):
                break

        if fig_num is not None:
            # Plot lines onto original image
            final_image = image.copy()
            for index in [i_left_line, i_right_line]:
                if index is not None:
                    x1, y1, x2, y2 = lines[i_left_line].flatten()
                    cv2.line(
                        img=final_image,
                        pt1=(x1, y1),
                        pt2=(x2, y2),
                        color=(240, 30, 20),
                        thickness=20
                    )

            is_left_found = i_left_line is not None
            is_right_found = i_right_line is not None
            image_infos = [
                {'image': image, 'title': 'Original', 'kwargs': {}},
                {'image': image_value, 'title': 'HSV - Value', 'kwargs': {'cmap': 'gray'}},
                {'image': image_blur, 'title': 'Value - Gaussian Blur', 'kwargs': {'cmap': 'gray'}},
                {'image': image_edges, 'title': 'Canny Edges', 'kwargs': {'cmap': 'gray'}},
                {'image': roi_mask, 'title': 'ROI Mask', 'kwargs': {'cmap': 'gray'}},
                {'image': threshold_mask, 'title': 'Original', 'kwargs': {'cmap': 'gray'}},
                {'image': image_edges_with_mask, 'title': 'Edges w/ ROI & Threshold Mask', 'kwargs': {'cmap': 'gray'}},
                {'image': final_image, 'title': f'Image w/ Lane Lines\nLeft/Right found? {is_left_found}/{is_right_found}', 'kwargs': {}},
            ]
            plt.figure(fig_num, clear=True, figsize=(8, 8))
            for ii, image_info in enumerate(image_infos):
                plt.subplot(3, 3, ii + 1)
                plt.imshow(image_info['image'], aspect='auto', **image_info['kwargs'])
                plt.title(image_info['title'])

            plt.tight_layout()

LaneDetector = LaneLineDetector(config={})
LaneDetector.run(
    image=image,
    road_to_cam_proj_mat=calib['Tr_cam_to_road:'],
    fig_num=1
)

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
