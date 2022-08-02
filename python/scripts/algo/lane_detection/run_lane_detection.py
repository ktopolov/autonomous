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

plt.figure(1, clear=True, figsize=(6, 8))
image_hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

channels = ['h', 's', 'v']
for ii, channel in enumerate(channels):
    plt.subplot(3, 1, ii + 1)
    plt.imshow(image_hsv[:, :, ii], aspect='auto', cmap='gray', vmin=0, vmax=255)
    plt.title(f'HSV Image - Channel: {channel} - Frame {frame_num}')
    plt.xlabel('Image x')
    plt.ylabel('Image y')

plt.tight_layout()

# Gaussian Blue Value Channel
image_blur = cv2.GaussianBlur(image_hsv[:, :, 2], (5, 5), 0)

plt.figure('Blur', clear=True)
plt.imshow(image_blur, aspect='auto', cmap='gray')
plt.title(f'Blurred Value Channel')
plt.xlabel('Image x')
plt.ylabel('Image y')

# %% Canny Edge Detection
low_threshold = 130
high_threshold = 200
edges = cv2.Canny(
    image_blur,
    low_threshold,
    high_threshold,
    apertureSize=3
)

# ROI
def region_of_interest(image):
    """Define polygon region of interest in image

    Args:
        image: (n_row, n_col)

    Returns:
        mask: (n_row, n_col) boolean mask
    """
    polygons = np.array([
        [(398, 375), (493, 181), (1231, 357)]
    ])
    mask = np.zeros_like(image)
    cv2.fillPoly(mask, polygons, 255)
    return mask

roi_mask = region_of_interest(edges)

edges_roi = roi_mask * edges

plt.figure('ROI Image', clear=True)
plt.imshow(roi_mask[:, :, np.newaxis] * image, aspect='auto')
plt.title('Image ROI')
plt.xlabel('Image x')
plt.ylabel('Image y')

plt.figure('ROI', clear=True)
plt.subplot(2, 2, 1)
plt.imshow(edges, aspect='auto', cmap='gray')
plt.title('Edges')
plt.xlabel('Image x')
plt.ylabel('Image y')

plt.subplot(2, 2, 2)
plt.imshow(roi_mask, aspect='auto', cmap='gray')
plt.title('ROI Mask')
plt.xlabel('Image x')
plt.ylabel('Image y')

plt.subplot(2, 2, 3)
plt.imshow(edges_roi, aspect='auto', cmap='gray')
plt.title(f'Edges in ROI')
plt.xlabel('Image x')
plt.ylabel('Image y')

# Threshold only for white pixels
threshold = 200
threshold_mask = image_hsv[:, :, 2] > threshold
edges_roi_thresholded = edges_roi * threshold_mask

plt.subplot(2, 2, 4)
plt.imshow(edges_roi_thresholded, aspect='auto', cmap='gray')
plt.title(f'Edges in ROI')
plt.xlabel('Image x')
plt.ylabel('Image y')

# %% Detect Lines
rho_res = 2  # pixels resolution
theta_res = 2.0  # degrees
accumulator_threshold = 10  # number of hits along line
lines = cv2.HoughLinesP(
    edges_roi_thresholded,
    rho_res,
    np.deg2rad(theta_res),
    threshold=accumulator_threshold,
    minLineLength=20,
    maxLineGap=10
)

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

if i_left_line is None:
    print('Could not find left line')
if i_right_line is None:
    print('Could not find right line')

plt.figure('Final', clear=True)
plt.imshow(image, aspect='auto')
xlim = np.array([0, n_col])
ylim = np.array([n_row, 0])
for i_line in [i_left_line, i_right_line]:
    if i_line is None:
        continue  # could not be found

    x1, y1, x2, y2 = lines[i_line, 0, :]
    slope = (y2 - y1) / (x2 - x1)
    intercept = y2 - slope * x2
    y_line = slope * xlim + intercept
    plt.plot(xlim, y_line, 'r--')

plt.xlim(xlim)
plt.ylim(ylim)
plt.title('Final')

# Project into real-world (assume road coordinate frame +z is normal to road, x/y in road)
cam_to_road = calib['Tr_cam_to_road:']
camera_matrix, rotmat_to_cam, tvec_world_to_cam = cv2.decomposeProjectionMatrix(cam_to_road)[:3]
tvec_world_to_cam = tvec_world_to_cam[:3] / tvec_world_to_cam[3]  # from homogeneous to cartesian

# FIXME-KT: Decompose this into camera and extrinsic matrices, rotate points via homography into
# road frame (augment pixels from 2D to 3D, apply 3D rotation homography, assign a depth and recover
# 3D point using https://medium.com/yodayoda/from-depth-map-to-point-cloud-7473721d3f)
#
# Then, report line slope and intercept in real-world (or rho/theta?)
plt.show()
