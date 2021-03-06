#
# Copyright (c) 2015, Nikolay Polyarnyi
# All rights reserved.
#

import asyncio
import logging
import cyglfw3 as glfw

from thermal.utils import support
from thermal.gui.helpers import FPSLimiter
from thermal.gui.frames.plot2d import Plot2D
from thermal.simulation import initial_generators
from thermal.simulation.processor import SimulationProcessor

logger = logging.getLogger(__name__)


class SimulationApp:

    def __init__(self, processor=None):
        self._plotter = Plot2D()
        self._processor = processor or SimulationProcessor()
        self._cpu_executor = support.AsyncExecutor(1)

        self._rendering = None
        self._simulation_daemon = None
        self._paused = None
        self._tics_limiter = None

        self._initial_function = None
        self._method_name = None
        self._params = None

        self._should_restart = False

        self._plotter.add_on_keyboard_callback(self._pause_cb)

    def start(self):
        self._rendering = support.wrap_exc(asyncio.ensure_future(self._plotter.render_loop()), logger)
        self._simulation_daemon = support.wrap_exc(asyncio.ensure_future(self._simulation()), logger)

    def setup(self, initial_function_name, method_name, params):
        self._initial_function = getattr(initial_generators, initial_function_name)
        self._method_name = method_name
        self._params = params
        self._should_restart = True
        if self._tics_limiter is not None:
            self._tics_limiter.update()
        if self._paused is not None:
            self._paused.set_result(True)

    def stop(self):
        self._plotter.close()
        if self._rendering is not None:
            self._rendering.cancel()
            self._rendering = None
        if self._simulation_daemon is not None:
            self._simulation_daemon.cancel()
            self._simulation_daemon = None

    def _pause_cb(self, window, key, scancode, action, mods):
        if self._paused is None and (action == glfw.PRESS and key == glfw.KEY_SPACE):
            self._pause()

    def _pause(self):
        print("Paused! Press SPACE to continue...")
        self._paused = asyncio.Future()

        def cb(window, key, scancode, action, mods):
            if action == glfw.PRESS and key == glfw.KEY_SPACE:
                print('Continue...')
                self._paused.set_result(True)
        self._plotter.add_on_keyboard_callback(cb)

        def cleanup(_):
            self._paused = None
            self._plotter.delete_on_keyboard_callback(cb)
        self._paused.add_done_callback(cleanup)

    @asyncio.coroutine
    def _wait_for_space(self):
        space_key = asyncio.Future()

        def cb(window, key, scancode, action, mods):
            if action == glfw.PRESS and key == glfw.KEY_SPACE:
                space_key.set_result(True)
        self._plotter.add_on_keyboard_callback(cb)
        space_key.add_done_callback(lambda f: self._plotter.delete_on_keyboard_callback(cb))
        yield from space_key

    @asyncio.coroutine
    def _simulation(self):
        while True:
            self._should_restart = False
            iters, n = self._params['iters'], self._params['n']
            dx, dt, u, chi = self._params['dx'], self._params['dt'], self._params['u'], self._params['chi']
            s, r = self._params['s'], self._params['r']

            ts = self._initial_function(n, n // 2)
            self._plotter.set_ys(ts)
            self._pause()
            self._tics_limiter = FPSLimiter(1 / self._params['view_dt'])

            while not self._should_restart:
                if self._paused is not None:
                    yield from self._paused
                ts = yield from self._cpu_executor.map(self._processor.process, ts, dx=dx, dt=dt, u=u, chi=chi, s=s, r=r,
                                                       method_name=self._method_name, iters=iters)
                self._plotter.set_ys(ts)
                yield from self._tics_limiter.ensure_frame_limit()
                # print('{:.1f} FPS'.format(tics_limiter.get_fps()))
