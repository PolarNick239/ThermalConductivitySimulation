#
# Copyright (c) 2015, Nikolay Polyarnyi
# All rights reserved.
#

import logging
import pkg_resources
from pathlib import Path

from thermal.utils import gl


logger = logging.getLogger(__name__)

textures_path = Path(pkg_resources.get_provider('thermal.gui.textures.resources').get_resource_filename(__name__, '.'))


class TexturesFactory:

    def __init__(self):
        self._textures_names = None

    def _detect_textures(self):
        self._textures_names = set()
        for path in textures_path.glob('*.png'):
            self._textures_names.add(path.name.split('.')[0])

    def get_textures_names(self):
        if self._textures_names is None:
            self._detect_textures()

        return sorted(self._textures_names)

    @staticmethod
    def create_texture(texture_name):
        path = textures_path / '{}.png'.format(texture_name)
        (w, h), texture = gl.create_image_texture(path)
        return (w, h), texture
