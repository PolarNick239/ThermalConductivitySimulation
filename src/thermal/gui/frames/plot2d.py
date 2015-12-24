#
# Copyright (c) 2015, Nikolay Polyarnyi
# All rights reserved.
#

import asyncio
import logging
import numpy as np

from thermal.utils import gl
from thermal.utils import support
from thermal.gui.frames.frame2d import Frame2D

logger = logging.getLogger(__name__)


class Plot2D(Frame2D):

    def __init__(self, width=640, height=480, title='Plot2D',
                 *, io_executor=None, fps_limit=0,
                 shaders_factory=None, textures_factory=None, loop=None):
        super(Plot2D, self).__init__(width, height, title,
                                     io_executor=io_executor, fps_limit=fps_limit,
                                     shaders_factory=shaders_factory, textures_factory=textures_factory, loop=loop)

        self._heat_map_texture = None
        self._plotting_shader = None
        ''':type: thermal.utils.gl.Shader'''

        self._ys = None

        self._used_ys = None
        self._ys_texture = None
        self._ys_values_range = None
        self._y_axis_range = None

    @asyncio.coroutine
    def init(self):
        yield from super(Plot2D, self).init()
        _, self._heat_map_texture = yield from self._gl_executor.map(self._textures_factory.create_texture, 'heatmap')
        self._plotting_shader = yield from self._gl_executor.map(self._shaders_factory.create_shader, 'plotting')

    @asyncio.coroutine
    def release(self):
        if self._heat_map_texture is not None:
            yield from self._gl_executor.map(self._heat_map_texture.release)
            self._heat_map_texture = None
        if self._ys_texture is not None:
            yield from self._gl_executor.map(self._ys_texture.release)
            self._ys_texture = None

    def set_ys(self, ys):
        self._ys = np.float32(ys)
        self.update()

    def set_ys_range(self, min_y, max_y):
        self._y_axis_range = (min_y, max_y)
        self.update()

    def _get_y_range(self):
        if self._y_axis_range is not None:
            return self._y_axis_range
        if self._ys_values_range is not None:
            if self._ys_values_range[0] == self._ys_values_range[1]:
                return self._ys_values_range[0] - 0.5, self._ys_values_range[1] + 0.5
            else:
                return self._ys_values_range
        return 0., 1.

    def _create_ys_texture(self):
        assert self._ys is not None
        # noinspection PyTypeChecker
        n = len(self._ys)
        texture = gl.Texture1D()
        with texture:
            texture.set_params(gl.LINEAR_LINEAR + gl.CLAMP_TO_EDGE + gl.NO_MIPMAPING + [(gl.GL_TEXTURE_BORDER_COLOR, [0.0, 0.0, 0.0, 0.0])])
            with gl.configure_pixel_store([(gl.GL_UNPACK_ALIGNMENT, 1)]):
                gl.glTexImage1D(texture.target, 0, gl.GL_R32F, n, 0, gl.GL_RED, gl.GL_FLOAT, self._ys)
        self._ys_texture = texture

    @asyncio.coroutine
    def prepare_for_render(self):
        super().prepare_for_render()
        if self._used_ys is not self._ys:
            self._used_ys = self._ys
            self._ys_values_range = self._ys.min(), self._ys.max()
            if self._ys_texture is not None:
                support.wrap_exc(asyncio.ensure_future(self._gl_executor.map(self._ys_texture.release)), logger)
            self._ys_texture = None

    def _render_scene(self):
        if self._ys is None:
            return
        if self._ys_texture is None:
            self._create_ys_texture()

        y_min, y_max = self._get_y_range()
        y_range = y_max - y_min
        view_y_min, view_y_max = y_min - y_range * 0.2, y_max + y_range * 0.2
        to_world_mtx = np.array([[0.5, 0, 0, 0.5],
                                 [0, 0.5 * (view_y_max - view_y_min), 0, (view_y_min + view_y_max) / 2.0],
                                 [0, 0, 1.0, 0],
                                 [0, 0, 0, 1.0]])

        with self._plotting_shader:
            self._plotting_shader.uniform_matrix_f('to_world_mtx', to_world_mtx)
            self._plotting_shader.uniform_f('y_range', (y_min, y_max))
            self._plotting_shader.uniform_f('line_width', 40.0 / self._height)
            self._plotting_shader.bind_textures(ys_tex=self._ys_texture, colormap_tex=self._heat_map_texture)

            screen_position = np.array([[-1.0, -1.0], [1.0, -1.0], [-1.0, 1.0], [1.0, 1.0]], np.float32)
            screen_position = np.hstack([screen_position, np.array([[0.0]] * 4), np.array([[1.0]] * 4)])
            gl.draw_attrib_arrays(gl.GL_TRIANGLES, indices=np.int32([[0, 1, 2], [1, 2, 3]]),
                                  screen_position=screen_position)


if __name__ == '__main__':
    frame = Plot2D()
    ys = np.arange(239.0)
    frame.set_ys(ys)
    frame.set_ys_range(-300, 300)
    asyncio.get_event_loop().run_until_complete(frame.render_loop())
