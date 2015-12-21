#
# Copyright (c) 2015, Nikolay Polyarnyi
# All rights reserved.
#

import asyncio
import logging
from concurrent.futures import CancelledError

import cyglfw3 as glfw
from abc import abstractmethod, ABCMeta

from thermal.gui.helpers import FPSLimiter
from thermal.gui.shaders.shaders_factory import ShadersFactory
from thermal.gui.textures.textures_factory import TexturesFactory
from thermal.utils import gl
from thermal.utils.gl import GLExecutor
from thermal.utils.gl_context import create_window, GLFWContext
from thermal.utils.support import AsyncExecutor

logger = logging.getLogger(__name__)


class Frame2D(metaclass=ABCMeta):

    def __init__(self, width=640, height=480, title='Frame2D',
                 *, io_executor=None, fps_limit=0,
                 shaders_factory=None, textures_factory=None, loop=None):
        self._loop = loop or asyncio.get_event_loop()
        self._io_executor = io_executor or AsyncExecutor(4, self._loop)
        self._shaders_factory = shaders_factory or ShadersFactory()
        self._textures_factory = textures_factory or TexturesFactory()

        self._width, self._height = width, height
        self._title = title
        self._viewport_actual = False
        self._window = create_window(self._width, self._height, title)
        self._gl_executor = GLExecutor(GLFWContext(self._window), self._loop)

        self._fps_limiter = FPSLimiter(0)

        self._simple_shader = None
        self._initialized = False

        self._on_keyboard_callbacks = set()

    @asyncio.coroutine
    def init(self):
        assert not self._initialized
        glfw.SetScrollCallback(self._window, self._on_scroll)
        glfw.SetKeyCallback(self._window, self._on_keyboard)

        glfw.SetWindowSizeCallback(self._window, self._on_resize)
        glfw.SetWindowCloseCallback(self._window, lambda window: self._fps_limiter.stop())

        yield from self._gl_executor.init_gl_context()

        self._shader = yield from self._gl_executor.map(self._shaders_factory.create_shader, 'simple')
        self._initialized = True

    def add_on_keyboard_callback(self, callback):
        self._on_keyboard_callbacks.add(callback)

    def delete_on_keyboard_callback(self, callback):
        self._on_keyboard_callbacks.remove(callback)

    def _on_scroll(self, window, x, y):
        pass

    def _on_keyboard(self, window, key, scancode, action, mods):
        # logger.debug('Keyboard: key={}, scancode={}, action={}, mods={}'.format(key, scancode, action, mods))
        if action == glfw.PRESS:
            pass

        for cb in self._on_keyboard_callbacks.copy():
            cb(window, key, scancode, action, mods)

    def _on_resize(self, window, width, height):
        logger.debug('Resize to {}x{}'.format(width, height))
        self._width, self._height = width, height
        self._viewport_actual = False
        self.update()

    def update(self):
        self._fps_limiter.update()

    def _gl_update_viewport(self):
        if not self._viewport_actual:
            gl.glViewport(0, 0, self._width, self._height)
            self._viewport_actual = True

    @abstractmethod
    def _render_scene(self):
        pass

    @asyncio.coroutine
    def prepare_for_render(self):
        pass

    def _render(self):
        self._gl_update_viewport()
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)
        gl.glClearColor(0.0, 0.0, 0.0, 1.0)
        gl.glEnable(gl.GL_DEPTH_TEST)
        gl.glClearDepth(1.0)
        gl.glClear(gl.GL_COLOR_BUFFER_BIT | gl.GL_DEPTH_BUFFER_BIT)

        self._render_scene()
        gl.glFinish()

    @asyncio.coroutine
    def render(self):
        yield from self.prepare_for_render()
        yield from self._gl_executor.map(self._render)

        glfw.SwapBuffers(self._window)

    @asyncio.coroutine
    def render_loop(self):
        if not self._initialized:
            yield from self.init()

        while not glfw.WindowShouldClose(self._window):
            try:
                yield from self._fps_limiter.ensure_frame_limit(glfw.PollEvents)
            except CancelledError:
                logger.info('Stopped! {}'.format(self._title))
                break

            yield from self.render()

    def close(self):
        glfw.DestroyWindow(self._window)
