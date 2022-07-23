"""Some sample script to run"""
# Standard Imports
import pathlib

# Third-Party Imports
import cv2

# Local Imports
from modules import sample_module

if __name__ == '__main__':
    my_path = pathlib.Path('.')
    print(f'Absolute path: {my_path.absolute()}')

    print(f'CV2 type: {cv2.CV_32FC3}')

    result = sample_module.add(1, 2)
    print(f'Sample module result: {result}')

