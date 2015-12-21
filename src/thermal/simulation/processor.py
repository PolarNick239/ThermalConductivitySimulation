#
# Copyright (c) 2015, Nikolay Polyarnyi
# All rights reserved.
#


import logging
import numpy as np
import pkg_resources
import pyopencl as cl
import pyopencl.array
from pathlib import Path

from thermal.utils.cl import create_context


logger = logging.getLogger(__name__)

kernels_path = Path(pkg_resources.get_provider('thermal.simulation.kernels').get_resource_filename(__name__, '.'))


class SimulationProcessor:

    def __init__(self, cl_context: cl.Context=None, kernels_cache_dir=None):
        self._context = cl_context
        self._programs = {}
        self._kernels_cache_dir = kernels_cache_dir

        self.compiled = False

    def compile(self):
        self._context = self._context or create_context()
        logger.debug('Compiling OpenCL kernels for SimulationProcessor...')

        common_code_path = kernels_path / 'common.cl'
        with common_code_path.open() as f:
            common_code = f.readlines()

        for cl_file in kernels_path.glob("**/*.cl"):
            if cl_file == common_code_path:
                continue

            name = cl_file.name.split(".")[0]
            with cl_file.open() as f:
                source_code = f.readlines()

            logger.debug('Building kernels for \'{}\'...'.format(name))
            self._programs[name] = cl.Program(self._context, ''.join(common_code + source_code))\
                .build(cache_dir=self._kernels_cache_dir)

        self.compiled = True
        logger.debug('OpenCL kernels for SimulationProcessor compiled: {}!'.format(self.get_method_names()))

    def process(self, ts,
                *, dx, dt, u, chi,
                iters=1, method_name: str) -> cl.array.Array:
        if not self.compiled:
            self.compile()

        program = self._programs[method_name]
        queue = cl.CommandQueue(self._context)

        n = len(ts)
        dx, dt, u, chi = map(np.float32, [dx, dt, u, chi])
        n = np.int32(n)

        if isinstance(ts, cl.array.Array):
            ts_cl = ts
        else:
            ts = np.float32(ts)
            ts_cl = cl.array.to_device(queue, ts)
        ts_res_cl = cl.array.zeros(queue, n, np.float32)

        dt_iter = np.float32(dt / n)
        for i in range(iters):
            program.iterate(queue, (n,), None,
                            ts_cl.data, ts_res_cl.data,
                            dx, dt_iter, u, chi,
                            n)
            ts_cl, ts_res_cl = ts_res_cl, ts_cl

        ts_res = ts_cl.get()
        return ts_res

    def get_method_names(self):
        if not self.compiled:
            self.compile()

        return sorted(self._programs.keys())
