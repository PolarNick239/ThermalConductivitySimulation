#
# Copyright (c) 2015, Nikolay Polyarnyi
# All rights reserved.
#

import numpy as np


def linear_peak_function(n, i, v_start=0, vi=1, v_end=0, dtype=np.float32):
    """
    >>> linear_peak_function(5, 2, v_start=3, vi=7, v_end=5)
    array([ 3.,  5.,  7.,  6.,  5.], dtype=float32)
    """
    xs = np.zeros(n, dtype)
    xs[:i + 1] = np.linspace(v_start, vi, i + 1)
    xs[i:] = np.linspace(vi, v_end, n - i)
    return xs


def step_function(n, i, before_value=1, after_value=0, dtype=np.float32):
    """
    >>> step_function(4, 0)
    array([ 0.,  0.,  0.,  0.], dtype=float32)
    >>> step_function(5, 2)
    array([ 1.,  1.,  0.,  0.,  0.], dtype=float32)
    >>> step_function(4, 4)
    array([ 1.,  1.,  1.,  1.], dtype=float32)
    """
    xs = np.zeros(n, dtype)
    xs[:i] = before_value
    xs[i:] = after_value
    return xs


def peak_function(n, i, peak_value=1, others_value=0, dtype=np.float32):
    """
    >>> peak_function(5, 0)
    array([ 1.,  0.,  0.,  0.,  0.], dtype=float32)
    >>> peak_function(4, 3)
    array([ 0.,  0.,  0.,  1.], dtype=float32)
    """
    xs = np.zeros(n, dtype)
    xs[:] = others_value
    xs[i] = peak_value
    return xs
