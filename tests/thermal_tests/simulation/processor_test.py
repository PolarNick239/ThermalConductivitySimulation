#
# Copyright (c) 2015, Nikolay Polyarnyi
# All rights reserved.
#

import logging
import unittest
import numpy as np

from thermal.simulation.processor import SimulationProcessor

logger = logging.getLogger(__name__)


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
                                                        'explicit_leapfrog',
                                                        'implicit_by_flow',
                                                        'implicit_central',
                                                        'implicit_counter_flow',
                                                        'test_simple_linear_cl',
                                                        'test_simple_linear_py'])

    def test_processor_linear(self):
        processor = SimulationProcessor()
        ts = np.arange(239239)
        for method_name in ['test_simple_linear_cl', 'test_simple_linear_py']:
            ts_res = processor.process(ts, dx=1.0, dt=1.0, u=0.2, chi=1.0,
                                          method_name=method_name, iters=10)
            self.assertTrue(np.allclose(ts, ts_res), msg="For {} method!".format(method_name))

    def test_processor_linear2(self):
        processor = SimulationProcessor()
        u = 0.3
        ts = self._create_random_array(239239)

        np_res = (u * ts[:-2] + ts[1:-1] + u * ts[2:]) / (u + 1 + u)

        for method_name in ['test_simple_linear_cl', 'test_simple_linear_py']:
            ts_res = processor.process(ts, dx=1.0, dt=1.0, u=u, chi=1.0,
                                       method_name=method_name)

            self.assertTrue(np.allclose(np_res, ts_res[1:-1]), msg="For {} method!".format(method_name))
            self.assertTrue(np.allclose(ts[[0, -1]], ts_res[[0, -1]]), msg="For {} method!".format(method_name))

    def test_all_methods_runnable(self):
        processor = SimulationProcessor()
        for method_name in processor.get_method_names():
            ts = self._create_random_array(239239)
            input_ts = ts.copy()

            logger.debug('Testing method: {}...'.format(method_name))
            ts_res = processor.process(input_ts, dx=1.0, dt=1.0, u=0.2, chi=1.0, method_name=method_name)

            self.assertTrue(np.all(~np.isnan(ts_res)), msg="For {} method!".format(method_name))
            self.assertTrue(np.allclose(ts_res[[0, -1]], ts[[0, -1]]), msg="Borders are not constant in {} method!".format(method_name))
            self.assertTrue(np.all(input_ts == ts), msg="{} method affects input!".format(method_name))
