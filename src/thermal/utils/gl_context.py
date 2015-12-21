#
# Copyright (c) 2015, Nikolay Polyarnyi
# All rights reserved.
#

import logging
import cyglfw3 as glfw
from abc import abstractmethod

from OpenGL.GL.VERSION.GL_1_0 import GL_TRUE, GL_FALSE

logger = logging.getLogger(__name__)


class GLContext:

    @abstractmethod
    def activate(self):
        pass

    @abstractmethod
    def deactivate(self):
        pass

    def __enter__(self):
        self.activate()

    def __exit__(self, type, value, traceback):
        self.deactivate()


def _error_callback(error_code, description):
    logger.error('GLFW error: {} {}'.format(error_code, description))
    raise Exception("GLFW error: {} {}!".format(error_code, description))

glfw.SetErrorCallback(_error_callback)

logger.debug('Initializing GLFW...')
if glfw.Init() != GL_TRUE:
    logger.error('GLFW initialization failed!')
    raise Exception("GLFW initialization failed!")
else:
    logger.debug('GLFW initialized!')

_NULL_WINDOW = glfw.Window()


def create_window(width=640, height=480, title='Monoceros'):
    window = glfw.CreateWindow(width, height, title)
    assert window is not None
    logger.debug('GLFW window created! ({}x{} "{}")'.format(width, height, title))
    return window


def _create_off_screen_window():
    glfw.WindowHint(glfw.VISIBLE, GL_FALSE)
    window = glfw.CreateWindow(239, 239, 'GLFW offscreen window for GL context')
    assert window is not None
    logger.debug('GLFW offscreen window for GL context created!')
    glfw.DefaultWindowHints()
    return window


class GLFWContext(GLContext):

    def __init__(self, window=None):
        if window is None:
            window = _create_off_screen_window()

        self._window = window

    def activate(self):
        glfw.MakeContextCurrent(self._window)

    def deactivate(self):
        glfw.MakeContextCurrent(_NULL_WINDOW)
