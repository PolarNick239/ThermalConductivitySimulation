
def solve(ts, s, r, dx, dt, u, chi, iters):
    ts_res = ts.copy()
    for i in range(iters):
        ts_res[1:-1] = (u * ts_res[:-2] + ts_res[1:-1] + u * ts_res[2:]) / (u + 1 + u)
    return ts_res
