"""Computer vision support functions"""
# Standard Imports
import typing
import warnings

# Third Party Imports
import numpy as np
import cv2


def augment(v: np.ndarray) -> np.ndarray:
    """Augment vector(s) with a '1' to excend dimension by one

    Args:
        v: input vector(s) of shape (..., N)

    Returns:
        out: Output vector(s) of shape (..., N + 1)
    """
    if np.ndim(v) == 1:
        out = np.append(v, 1)
    else:
        front_shape = v.shape[:-1]
        ones_vec = np.ones(front_shape)
        out = np.concatenate((v, ones_vec[:, np.newaxis]), axis=-1)
    return out


def homo_to_cart(v_homo: np.ndarray) -> np.ndarray:
    """Convert homogeneous coordinate vector(s) to cartesian

    Args:
        v_homo: Input homogeneous vector(s) (..., N+1)

    Returns:
        v_out: Output cartesian vector(s) (..., N)
    """
    v_out = v_homo[..., :-1] / v_homo[..., -1][..., np.newaxis]
    return v_out


def apply_perspective_transform(v: np.ndarray, transform: np.ndarray) -> np.ndarray:
    """Apply a perspective transformation (one dimension higher)

    Args:
        v: (..., N) input vector(s)
        transform: (..., N+1, N+1) transformation matrix(es)

    Returns:
        out: (..., N) output transformed vectors
    """
    aug = augment(v)
    out = np.einsum("...ij, ...j -> ...i", transform, aug)
    out = homo_to_cart(out)
    return out


def decompose_projection_matrix(
    world_to_cam_proj_matrix: np.ndarray,
) -> typing.Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Decompose projection matrix

    Args:
        world_to_cam_proj_matrix: (3, 4) projection matrix = K * [R | t]

    Returns:
        camera_matrix: (3, 3) Intrinsic camera projection matrix
        rot_world_to_cam: (3, 3) Rotation matrix from world frame to camera frame
        tvec_world_to_cam: (3,) Translation vector from world to camera
    """
    warnings.warn(
        "computer_vision.py: decompose_projection_matrix(): This function may not be correct"
    )
    (
        camera_matrix,
        rot_world_to_cam,
        tvec_world_to_cam_homo,
    ) = cv2.decomposeProjectionMatrix(world_to_cam_proj_matrix)[:3]
    tvec_world_to_cam_homo = tvec_world_to_cam_homo.flatten()  # from (4, 1) to (4,)
    tvec_world_to_cam = homo_to_cart(tvec_world_to_cam_homo)
    return camera_matrix, rot_world_to_cam, tvec_world_to_cam
