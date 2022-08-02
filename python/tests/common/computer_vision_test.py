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
    v = np.array([
        [1.1, 2.2, 3.3],
        [4.4, 5.5, 6.6]
    ])
    out = cvision.augment(v)
    correct = np.array([
        [1.1, 2.2, 3.3, 1],
        [4.4, 5.5, 6.6, 1]
    ])
    np.testing.assert_array_equal(out, correct)
