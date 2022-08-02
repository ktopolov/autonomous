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
frame_num = 0
image, calib_df = read_kitti_road_data(
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

# %% Threshold
threshold = 200
thresholded = image_hsv[:, :, 2] > threshold

plt.figure('Thresholded', clear=True)
plt.imshow(thresholded, aspect='auto', cmap='gray')
plt.title(f'Thresholded Value Channel - Threshold: {threshold}')
plt.xlabel('Image x')
plt.ylabel('Image y')

print('Done')

# %% Crop ROI
n_row, n_col = thresholded.shape
start_row = 200
n_roi_row = n_row - start_row
n_roi_col = 600
start_col = (n_col - n_roi_col) // 2

stop_row = start_row + n_roi_row
stop_col = start_col + n_roi_col

roi = thresholded[start_row:stop_row, start_col:stop_col]
roi = roi.astype(np.uint8)

# %% Erosion to Remove Noisy Points
# Creating kernel
erode_shape = (3, 3)
kernel = np.ones(erode_shape, np.uint8)  # take minimum of values in this kernel window
roi_eroded = cv2.erode(roi, kernel)

dilate_shape = (5, 5)
kernel = np.ones(dilate_shape, np.uint8)  # take minimum of values in this kernel window
roi_dilated = cv2.dilate(roi_eroded, kernel) 

plt.figure('ROI', clear=True)
plt.subplot(3, 1, 1)
plt.imshow(roi, aspect='auto', cmap='gray')
plt.title(f'ROI')
plt.xlabel('Image x')
plt.ylabel('Image y')

plt.subplot(3, 1, 2)
plt.imshow(roi_eroded, aspect='auto', cmap='gray')
plt.title(f'ROI - Eroded')
plt.xlabel('Image x')
plt.ylabel('Image y')

plt.subplot(3, 1, 3)
plt.imshow(roi_dilated, aspect='auto', cmap='gray')
plt.title(f'ROI - Dilated')
plt.xlabel('Image x')
plt.ylabel('Image y')

# %% Detect Edges and Lines
fullsize = np.zeros_like(image_hsv[:, :, 0])
fullsize[start_row:stop_row, start_col:stop_col] = roi_dilated
edges = cv2.Canny(image_hsv[:, :, 2], 100, 150, apertureSize=3)

edges = edges * fullsize

plt.figure('Edges', clear=True)
plt.imshow(edges, aspect='auto', cmap='gray')
plt.title(f'Edges')
plt.xlabel('Image x')
plt.ylabel('Image y')

# This returns an array of r and theta values
# rho: Distance (pixels) resolution to sweep
# theta: Angular (deg) resolution to sweep
# threshold: Number of hits to declare line
# lines = cv2.HoughLines(edges, rho=1, theta=np.pi/180, threshold=20)
lines = cv2.HoughLines(edges, rho=1, theta=np.pi/30, threshold=20)

# The below for loop runs till r and theta values
# are in the range of the 2d array
for r_theta in lines:
    arr = np.array(r_theta[0], dtype=np.float64)
    r, theta = arr
    # Stores the value of cos(theta) in a
    a = np.cos(theta)
 
    # Stores the value of sin(theta) in b
    b = np.sin(theta)
 
    # x0 stores the value rcos(theta)
    x0 = a*r
 
    # y0 stores the value rsin(theta)
    y0 = b*r
 
    # x1 stores the rounded off value of (rcos(theta)-1000sin(theta))
    x1 = int(x0 + 1000*(-b))
 
    # y1 stores the rounded off value of (rsin(theta)+1000cos(theta))
    y1 = int(y0 + 1000*(a))
 
    # x2 stores the rounded off value of (rcos(theta)+1000sin(theta))
    x2 = int(x0 - 1000*(-b))
 
    # y2 stores the rounded off value of (rsin(theta)-1000cos(theta))
    y2 = int(y0 - 1000*(a))
 
    # cv2.line draws a line in img from the point(x1,y1) to (x2,y2).
    # (0,0,255) denotes the colour of the line to be
    # drawn. In this case, it is red.
    cv2.line(image, (x1, y1), (x2, y2), (0, 0, 255), 2)

plt.figure('Detected Lines', clear=True)
plt.imshow(image, aspect='auto')
plt.title('Detected Lines')

plt.show()
