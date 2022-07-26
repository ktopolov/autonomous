"""Run data from kitti odometry dataset found at
https://www.kaggle.com/datasets/hocop1/kitti-odometry?select=sequences
with examples for usage found at
https://github.com/FoamoftheSea/KITTI_visual_odometry/blob/main/functions_codealong.ipynb

The original dataset came with:
    - 2 grayscale cameras, image_0, image_1 folders (omitted). P0, P1 for these in calib file
    - 2 RGB cameras, image_2, image_3 folders (omitted). P2, P3 for these in calib file
    - LiDAR (velodyne) with data and Tr row of calibr file

We only use the 2 RGB cameras here
"""
import pathlib
import os
from re import M
import typing
from cv2 import INTER_LINEAR

import matplotlib.pyplot as plt
import cv2
import numpy as np
import pandas as pd

# %% HELPERS
def decompose_projection_matrix(
    p: np.ndarray
) -> typing.Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Wrapper for opencv function to decompose projection matrix (extrinsic and intrinsic
    calibration info) into their invididual components

    Args:
        p: (3, 4) projection matrix defined by (camera_matrix * [world_to_cam | t_vec]) where K is
           the (3, 3) intrinsic camera calibration matrix, R is the rotation matrix from world to
           camera coords, and t = -R * (p_camera_world) is the translation

    Returns:
        camera_matrix: 
    """    
    camera_matrix, world_to_cam, t_vec_homo, _, _, _, _ = cv2.decomposeProjectionMatrix(p)
    t_vec = (t_vec_homo / t_vec_homo[3])[:3]
    return camera_matrix, world_to_cam, t_vec


# Configure
kitti_folder = pathlib.Path(f'/mnt/c/Users/ktopo/Desktop/kitti_odometry')
i_sequence = 0
i_frame = 0

# Get paths
sequence_folder = kitti_folder / f'sequences/{i_sequence:02d}'
time_path = sequence_folder / 'times.txt'
calib_path = sequence_folder / 'calib.txt'
left_image_path = sequence_folder / f'image_2/{i_sequence:06d}.png'
right_image_path = sequence_folder / f'image_3/{i_sequence:06d}.png'
pose_path = kitti_folder / 'poses' / f'{i_sequence:02d}.txt'

# Load info from paths
left_image = cv2.imread(str(left_image_path))
right_image = cv2.imread(str(right_image_path))

plt.figure(1, clear=True, figsize=(10, 6))
plt.subplot(2, 1, 1)
plt.imshow(left_image, aspect='auto')
plt.title('Left Image')

plt.subplot(2, 1, 2)
plt.imshow(right_image, aspect='auto')
plt.title('Right Image')

time_df = pd.read_csv(time_path, delimiter=' ', header=None)
time_df.columns = ['time']
time = time_df['time'].values[i_frame]

# DEFINE COORDINATE FRAMES:
# 1) World frame: _world
# 2) Robot frame: _robof
# 3) Left Camera Frame: _lframe
# 4) Right Camera Frame: _rframe

# Poses stored as K * [R | t] which is 3x4 matrix that can be decomposed
pose_df = pd.read_csv(pose_path, delimiter=' ', header=None)
truth_pose = np.array(pose_df.iloc[i_frame]).reshape((3, 4))

# Calibration info (camera position/orientation). Only stored once (not per-frame) which means
# it is likely relative to the vehicle's local frame (relative to the truth pose)
calib = pd.read_csv(calib_path, delimiter=' ', header=None, index_col=0)
left_proj_matrix = np.array(calib.loc['P2:']).reshape((3, 4))
right_proj_matrix = np.array(calib.loc['P3:']).reshape((3, 4))

# Decompose projection (calibraiton) matrices into components.
left_cam_mat, rot_robof_to_lframe, tvec_robof_to_lframe = decompose_projection_matrix(
    left_proj_matrix
)
tvec_robof_to_lframe = tvec_robof_to_lframe.flatten()

right_cam_mat, rot_robof_to_rframe, tvec_robof_to_rframe = decompose_projection_matrix(
    right_proj_matrix
)
tvec_robof_to_rframe = tvec_robof_to_rframe.flatten()

# Get equivalent rodrigues rotation vectors

# Define [R | t] relative transformations from left to right camera frame.
# Normally can use cv2.composeRT but since rotations are zero it seems to work strangely
# rvec_robof_to_lframe = cv2.Rodrigues(rot_robof_to_lframe)[0]
# rvec_robof_to_rframe = cv2.Rodrigues(rot_robof_to_rframe)[0]
# rvec_lframe_to_rframe, tvec_lframe_to_rframe = cv2.composeRT(
#     rvec1=rvec_robof_to_lframe,
#     tvec1=tvec_robof_to_lframe,
#     rvec2=rvec_robof_to_rframe,
#     tvec2=tvec_robof_to_rframe
# )[:2]

# Get each camera positions in robot frame. Since t_vec = -world_to_cam * p_cam_world
# We can invertt and get p_cam_world = -(world_to_cam^-1) * t_vec
p_lcam_robof = -np.linalg.solve(rot_robof_to_lframe, tvec_robof_to_lframe)
p_rcam_robof = -np.linalg.solve(rot_robof_to_rframe, tvec_robof_to_rframe)

rot_lframe_to_rframe = np.matmul(rot_robof_to_lframe.T, rot_robof_to_rframe)
p_rcam_lframe = np.einsum(
    'ij, j -> i',
    rot_robof_to_lframe,
    p_rcam_robof - p_lcam_robof
)
tvec_lframe_to_rframe = - np.einsum('ij, j -> i', rot_lframe_to_rframe, p_rcam_lframe)
transform_lframe_to_rframe = np.concatenate(
    (rot_lframe_to_rframe, tvec_lframe_to_rframe[:, np.newaxis]),
    axis=-1,
)

# Rectify image suck that both image planes have same orientation, and +x direction is along
# baseline
n_row, n_col, _ = left_image.shape
orig_shape = (n_col, n_row)
new_shape = orig_shape

rot_lframe_to_lframerect, rot_rframe_to_rframerect = cv2.stereoRectify(
    cameraMatrix1=left_cam_mat,
    distCoeffs1=None,
    cameraMatrix2=right_cam_mat,
    distCoeffs2=None,
    imageSize=orig_shape,
    R=rot_lframe_to_rframe,
    T=tvec_lframe_to_rframe,
    flags=cv2.CALIB_ZERO_DISPARITY,
    newImageSize=new_shape
)[:2]

new_camera_matrix = left_cam_mat.copy()
map_left_x, map_left_y = cv2.initUndistortRectifyMap(
    cameraMatrix=left_cam_mat,
    distCoeffs=None,
    R=rot_lframe_to_lframerect,
    newCameraMatrix=new_camera_matrix,
    size=new_shape,
    m1type=cv2.CV_32FC1
)
map_right_x, map_right_y = cv2.initUndistortRectifyMap(
    cameraMatrix=right_cam_mat,
    distCoeffs=None,
    R=rot_rframe_to_rframerect,
    newCameraMatrix=new_camera_matrix,
    size=new_shape,
    m1type=cv2.CV_32FC1
)

left_image_rect = cv2.remap(
    src=left_image,
    map1=map_left_x,
    map2=map_left_y,
    interpolation=cv2.INTER_LINEAR
)
right_image_rect = cv2.remap(
    src=right_image,
    map1=map_right_x,
    map2=map_right_y,
    interpolation=cv2.INTER_LINEAR
)

plt.figure(2, clear=True, figsize=(10, 6))
plt.subplot(2, 1, 1)
plt.imshow(left_image_rect, aspect='auto')
plt.title('Rectified Left Image')

plt.subplot(2, 1, 2)
plt.imshow(right_image_rect, aspect='auto')
plt.title('Rectified Right Image')

# Now that images are stereo-aligned, we can find matches and disparities
left_image_rect_grey = cv2.cvtColor(left_image_rect, cv2.COLOR_BGR2GRAY)
right_image_rect_grey = cv2.cvtColor(right_image_rect, cv2.COLOR_BGR2GRAY)

stereo = cv2.StereoSGBM_create(minDisparity=1, numDisparities=10, blockSize=21)
disparity = stereo.compute(left_image_rect_grey, right_image_rect_grey)

# TODO-KT: Recover depth from disparities and then transform into robot coordinates
# and then world coordinates
baseline_length = np.linalg.norm(p_lcam_robof - p_rcam_lframe)
focal_length = new_camera_matrix[0, 0]  # take x focal length since disparity in x-direction
depth = (baseline_length * focal_length) / disparity

plt.figure(3, clear=True, figsize=(10, 6))
plt.subplot(2, 1, 1)
plt.imshow(disparity, cmap='gray', aspect='auto')
plt.title('Disparity')
plt.colorbar()

plt.subplot(2, 1, 2)
plt.imshow(depth, cmap='gray', aspect='auto')
plt.title('Depth (m)')
plt.colorbar()

# Take left rectified image grayscale as baseline, and then add more and more
# red in the closer objects are
base_image = np.repeat(
    left_image_rect_grey[:, :, np.newaxis],
    repeats=3,
    axis=-1
)

norm_disparity = disparity.copy()
norm_depth = np.maximum(norm_disparity, 0)  # negative disparity should not be possible
norm_depth = (norm_depth - norm_depth.min()) / (norm_depth.max() - norm_depth.min())
norm_depth = (255 * norm_depth).astype(np.uint8)
base_image[:, :, 0] += norm_depth

plt.figure(4, clear=True, figsize=(10, 6))
plt.imshow(base_image, aspect='auto')
plt.title('Base Image Overlaid with Depth')

plt.figure(5, clear=True)
bins = np.histogram_bin_edges(disparity.flatten())
plt.hist(disparity.flatten(), bins=bins)
plt.title('Disparity Histogram')

plt.show(block=True)

