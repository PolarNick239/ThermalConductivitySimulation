#line 1

__kernel void init(__global const float * ts,
                    __global       float * ts_res,
                                   float s,
                                   float r,
                                   float dx,
                                   float dt,
                                   float u,
                                   float chi,
                                   int n
                    ) {
    int i = (int) get_global_id(0);
    if (i == 0 || i == n - 1) {
        ts_res[i] = ts[i];
        return;
    }

    // Iteration #0 as in explicit central scheme:
    ts_res[i] = ts[i] * (1 - 2 * r) + (r - s / 2.0f) * ts[i + 1] + (r + s / 2.0f) * ts[i - 1];
}


__kernel void solve(__global const float * ts_prev,
                    __global const float * ts,
                    __global       float * ts_res,
                                   float s,
                                   float r,
                                   float dx,
                                   float dt,
                                   float u,
                                   float chi,
                                   int n
                    ) {
    int i = (int) get_global_id(0);
    if (i == 0 || i == n - 1) {
        ts_res[i] = ts[i];
        return;
    }

    float ts_i_prev = ts_prev[i];
    ts_res[i] = ts_i_prev - ts[i] * 4 * r + (2 * r - s) * ts[i + 1] + (2 * r + s) * ts[i - 1];
}
