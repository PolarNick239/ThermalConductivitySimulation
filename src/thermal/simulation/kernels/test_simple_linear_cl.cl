#line 1

__kernel void solve(__global const float * ts,
                    __global       float * ts_res,
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

    for (int iter = 0; iter < iters; ++iter) {
        ts_res[i] = (u * ts[i - 1] + ts[i] + u * ts[i + 1]) / (u + 1 + u);
    }
}
