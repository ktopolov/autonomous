"""Sample test file for pytest"""
import numpy as np

def test_sample1():
    """First sample test"""
    print("Hello")
    assert True

def test_sample2():
    """Second sample test; setup to fail"""
    a = np.array([1, 2, 3])
    b = np.array([1, 4, 3])
    np.testing.assert_array_equal(a, b)

