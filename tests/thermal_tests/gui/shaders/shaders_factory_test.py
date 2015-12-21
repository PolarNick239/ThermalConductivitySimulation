#
# Copyright (c) 2015, Nikolay Polyarnyi
# All rights reserved.
#

import unittest

from thermal_tests import test_support
from thermal.utils.gl import GLExecutor
from thermal.gui.shaders.shaders_factory import ShadersFactory


class ShadersFactoryTest(unittest.TestCase):

    def test_shaders_names(self):
        factory = ShadersFactory()
        self.assertEqual(factory.get_shaders_names(), ['plotting', 'simple'])

    @test_support.run_until_complete
    def test_shaders_compilation(self):
        factory = ShadersFactory()
        gl_executor = GLExecutor()
        for shader_name in factory.get_shaders_names():
            yield from gl_executor.map(factory.create_shader, shader_name)
