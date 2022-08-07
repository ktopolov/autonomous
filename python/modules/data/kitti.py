"""Functions and code relating to working with KITTI datasets"""
# Standard Imports
import pathlib
import typing

# Third Party Imports
import numpy as np
import pandas as pd
import cv2


# %% KITTI ROAD DATASET
def read_calib_to_dict(
    path: typing.Union[str, pathlib.Path]
) -> dict:
    """Read calibration text file from KITTI dataset into dictionary

    Args:
        calib_path: Path to calibration .txt. file

    Returns:
        calib: Dictionary of calibration parameters
    """
    calib_df = pd.read_csv(path, delimiter=" ", header=None, index_col=0)
    calib = {
        index: np.array(calib_df.loc[index]).reshape((3, 4))
        for index in calib_df.index.values.tolist()
    }
    return calib


def read_kitti_road_data(
    data_road_path: pathlib.Path, data_type: str = "training", frame_num: int = 0
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
    assert data_type in ["training", "testing"], "Unknown data type"
    image_path = data_road_path / f"{data_type}/image_2/um_{frame_num:06d}.png"
    image = cv2.imread(str(image_path))

    # Load calibration
    calib_path = data_road_path / f"{data_type}/calib/um_{frame_num:06d}.txt"
    calib_df = pd.read_csv(calib_path, delimiter=" ", header=None, index_col=0)

    calib = {
        index: np.array(calib_df.loc[index]).reshape((3, 4))
        for index in calib_df.index.values.tolist()
    }

    return image, calib
