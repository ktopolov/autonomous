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
