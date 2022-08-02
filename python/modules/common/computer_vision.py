"""Computer vision support functions"""
# Third Party Imports
import numpy as np

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
