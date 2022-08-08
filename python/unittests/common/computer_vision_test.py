"""Unit tests for computer_vision.py"""
# Third Party Imports
import numpy as np

# Local Imports
from modules.common import computer_vision as cvision


def test_augment():
    """Unit test for computer_vision.augment()"""
    # Test 1
    out = cvision.augment(np.array([1, 2, 3]))
    np.testing.assert_array_equal(out, np.array([1, 2, 3, 1]))

    # Test 2
    v = np.array([[1.1, 2.2, 3.3], [4.4, 5.5, 6.6]])
    out = cvision.augment(v)
    correct = np.array([[1.1, 2.2, 3.3, 1], [4.4, 5.5, 6.6, 1]])
    np.testing.assert_array_equal(out, correct)


def test_homo_to_cart():
    """Unit test for computer_vision.homo_to_cart()"""
    v_in = np.array([1.0, 2.0, 2.0])
    v_out = cvision.homo_to_cart(v_in)
    v_out_correct = np.array([0.5, 1.0])
    np.testing.assert_array_equal(v_out, v_out_correct)


def test_apply_perspective_transform():
    """Unit test for computer_vision.homo_to_cart()"""
    v_in = np.array([2.0, 1.0])
    transform = np.array(
        [
            [np.sqrt(2) / 2, np.sqrt(2) / 2, 0.0],
            [np.sqrt(2) / 2, -np.sqrt(2) / 2, 0.0],
            [0.0, 0.0, 1.0],
        ]
    )
    v_out = cvision.apply_perspective_transform(v=v_in, transform=transform)
    v_out_correct = np.array([2.12132, 0.707107])
    np.testing.assert_array_almost_equal(v_out, v_out_correct)
