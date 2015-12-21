#line 1

__kernel void iterate(__global const float * ts,
                      __global       float * ts_res,
                                     float dx,
                                     float dt,
                                     float u,
                                     float chi,
                                     int n
                      ) {
    int i = (int) get_global_id(0);
    float s = u * dt / dx;
    float r = chi * dt / (dx * dx);

    if (i == 0 || i == n - 1) {
        ts_res[i] = ts[i];
        return;
    }

    ts_res[i] = ts[i] * (1 - 2 * r) + (r - s / 2.0f) * ts[i + 1] + (r + s / 2.0f) * ts[i - 1];
}
