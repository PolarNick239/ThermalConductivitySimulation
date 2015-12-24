#
# Copyright (c) 2015, Nikolay Polyarnyi
# All rights reserved.
#

import sys
import logging
import itertools
import numpy as np
import pkg_resources
import pyopencl as cl
import pyopencl.array
from pathlib import Path
from importlib import import_module

from thermal.utils.cl import create_context


logger = logging.getLogger(__name__)

kernels_path = Path(pkg_resources.get_provider('thermal.simulation.kernels').get_resource_filename(__name__, '.'))


class SimulationProcessor:

    def __init__(self, cl_context: cl.Context=None, kernels_cache_dir=None):
        self._context = cl_context
        self._cl_methods = {}
        self._py_methods = {}
        self._kernels_cache_dir = kernels_cache_dir

        self.compiled = False

    def compile(self):
        self._context = self._context or create_context()
        logger.debug('Compiling OpenCL kernels for SimulationProcessor...')

        for cl_file in kernels_path.glob("*.cl"):
            name = cl_file.name.split(".")[0]
            with cl_file.open() as f:
                source_code = f.readlines()

            logger.debug('Building kernels for \'{}\'...'.format(name))
            self._cl_methods[name] = cl.Program(self._context, ''.join(source_code)).build(cache_dir=self._kernels_cache_dir)
        logger.debug('OpenCL kernels for SimulationProcessor compiled: {}!'.format(sorted(self._cl_methods.keys())))

        for py_file in kernels_path.glob("*.py"):
            if py_file.name.startswith("_"):
                continue

            name = py_file.name.split('.')[0]
            package = sys.modules[__name__]
            kernel_module = import_module('..kernels.{}'.format(name), package.__name__)
            solve = getattr(kernel_module, 'solve')
            self._py_methods[name] = solve
        logger.debug('Python kernels for SimulationProcessor imported: {}!'.format(sorted(self._py_methods.keys())))

        for name in self._cl_methods.keys():
            assert name not in self._py_methods.keys()
        for name in self._py_methods.keys():
            assert name not in self._cl_methods.keys()

        self.compiled = True

    def process(self, ts,
                *, dx, dt, u, chi, s=None, r=None,
                iters=1, method_name: str) -> cl.array.Array:
        n, iter_dt = len(ts), dt / iters
        if s is None:
            s = u * dt / dx
        if r is None:
            r = chi * dt / (dx * dx)

        if method_name in self._py_methods:
            solve = self._py_methods[method_name]
            ts_res = solve(ts, s, r, dx, dt / iters, u, chi, iters)
            return ts_res

        if not self.compiled:
            self.compile()

        program = self._cl_methods[method_name]
        queue = cl.CommandQueue(self._context)

        s, r, dx, dt, iter_dt, u, chi = map(np.float32, [s, r, dx, dt, iter_dt, u, chi])
        iters, n = map(np.int32, [iters, n])

        iter_dt = np.float32(dt / iters)

        if isinstance(ts, cl.array.Array):
            ts_cl = ts
        else:
            ts = np.float32(ts)
            ts_cl = cl.array.to_device(queue, ts)
        ts_res_cl = cl.array.zeros(queue, n, np.float32)

        program.solve(queue, (n,), None,
                      ts_cl.data, ts_res_cl.data,
                      s, r, dx, iter_dt, u, chi,
                      iters, n)

        ts_res = ts_res_cl.get()
        return ts_res

    def get_method_names(self):
        if not self.compiled:
            self.compile()

        return sorted(itertools.chain(self._cl_methods.keys(), self._py_methods.keys()))
