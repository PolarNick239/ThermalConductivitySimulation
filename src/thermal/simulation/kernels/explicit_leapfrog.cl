#line 1

__kernel void solve(__global const float * ts,
                    __global       float * ts_res,
                                   float s,
                                   float r,
                                   float dx,
                                   float dt,
                                   float u,
                                   float chi,
                                   int iters,
                                   int n
                    ) {
    int i = (int) get_global_id(0);
    if (i == 0 || i == n - 1) {
        ts_res[i] = ts[i];
        return;
    }

    float ts_i_prev = ts_res[i];
    float ts_i_cur = NAN;
    // Iteration #0 as in explicit central scheme:
    ts_res[i] = ts[i] * (1 - 2 * r) + (r - s / 2.0f) * ts[i + 1] + (r + s / 2.0f) * ts[i - 1];

    for (int iter = 1; iter < iters; ++iter) {
        ts_i_cur = ts_res[i];
        ts_res[i] = ts_i_prev - ts_res[i] * 4 * r + (2 * r - s) * ts_res[i + 1] + (2 * r + s) * ts_res[i - 1];
        ts_i_prev = ts_i_cur;
    }
}
