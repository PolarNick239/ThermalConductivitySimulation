#
# Copyright (c) 2015, Nikolay Polyarnyi
# All rights reserved.
#

import unittest

from thermal_tests import test_support
from thermal.utils.gl import GLExecutor
from thermal.gui.textures.textures_factory import TexturesFactory


class TexturesFactoryTest(unittest.TestCase):

    def test_textures_names(self):
        factory = TexturesFactory()
        self.assertEqual(factory.get_textures_names(), ['heatmap'])

    @test_support.run_until_complete
    def test_textures_construction(self):
        factory = TexturesFactory()
        gl_executor = GLExecutor()
        for texture_name in factory.get_textures_names():
            (w, h), texture = yield from gl_executor.map(factory.create_texture, texture_name)
            yield from gl_executor.map(texture.release)
