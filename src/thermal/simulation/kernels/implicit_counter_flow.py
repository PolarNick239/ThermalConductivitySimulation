import numpy as np
from scipy.linalg import solve_banded

from thermal.utils import support


def solve(ts, s, r, dx, dt, u, chi, iters):
    n = len(ts)

    lower_diag = support.np_the_same(n, -(s + r), np.float32)
    diag = support.np_the_same(n, (1 + s + 2 * r), np.float32)
    upper_diag = support.np_the_same(n, -r, np.float32)

    # Out of bounds values should be zero, and borders are constant
    upper_diag[[0, 1]] = 0
    diag[[0, -1]] = 1
    lower_diag[[-1, -2]] = 0

    diags = np.array([upper_diag, diag, lower_diag])

    for i in range(iters):
        ts = solve_banded((1, 1), diags, ts)

    return ts
