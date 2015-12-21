#
# Copyright (c) 2015, Nikolay Polyarnyi
# All rights reserved.
#

import logging
import pkg_resources
from pathlib import Path

from thermal.utils import gl


logger = logging.getLogger(__name__)

shaders_path = Path(pkg_resources.get_provider('thermal.gui.shaders').get_resource_filename(__name__, '.'))


class ShadersFactory:

    def __init__(self):
        self._shaders_names = None

    def _detect_shaders(self):
        self._shaders_names = set()
        for subdir in shaders_path.iterdir():
            if not subdir.is_dir() or subdir.name.startswith('_'):
                continue
            self._shaders_names.add(subdir.name)

    def get_shaders_names(self):
        if self._shaders_names is None:
            self._detect_shaders()

        return sorted(self._shaders_names)

    def _get_lines(self, shader_name, file_name):
        with (shaders_path / shader_name / '{}.glsl'.format(file_name)).open() as f:
            return f.readlines()

    def create_shader(self, shader_name):
        common_lines = self._get_lines(shader_name, 'common')
        vertex_lines = self._get_lines(shader_name, 'vertex')
        fragment_lines = self._get_lines(shader_name, 'fragment')

        shader = gl.Shader(''.join(common_lines + vertex_lines), ''.join(common_lines + fragment_lines), 400, 400)
        return shader
