#
# Copyright (c) 2015, Nikolay Polyarnyi
# All rights reserved.
#

import unittest
import numpy as np

from thermal.simulation.processor import SimulationProcessor


class SimulationProcessorTest(unittest.TestCase):

    def _create_random_array(self, n, seed=239):
        np.random.seed(seed)
        # noinspection PyArgumentList
        xs = np.random.rand(239239)
        return xs

    def test_methods_names(self):
        processor = SimulationProcessor()
        self.assertEqual(processor.get_method_names(), ['explicit_by_flow',
                                                        'explicit_central',
                                                        'explicit_counter_flow',
                                                        'test_simple_linear'])

    def test_processor_linear(self):
        processor = SimulationProcessor()
        ts = np.arange(239239)
        ts_res = processor.process(ts, dx=1.0, dt=1.0, u=0.2, chi=1.0,
                                      method_name='test_simple_linear', iters=10)
        self.assertTrue(np.allclose(ts, ts_res))

    def test_processor_linear2(self):
        processor = SimulationProcessor()
        u = 0.3
        ts = self._create_random_array(239239)

        np_res = (u * ts[:-2] + ts[1:-1] + u * ts[2:]) / (u + 1 + u)

        ts_res = processor.process(ts, dx=1.0, dt=1.0, u=u, chi=1.0,
                                      method_name='test_simple_linear')

        self.assertTrue(np.allclose(np_res, ts_res[1:-1]))
        self.assertTrue(np.allclose(ts[[0, -1]], ts_res[[0, -1]]))

    def test_all_methods_runnable(self):
        processor = SimulationProcessor()
        for method_name in processor.get_method_names():
            ts = self._create_random_array(239239)
            ts_res = processor.process(ts, dx=1.0, dt=1.0, u=0.2, chi=1.0, method_name=method_name)
            self.assertTrue(np.all(~np.isnan(ts_res)))
