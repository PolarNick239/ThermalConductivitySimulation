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

    def __init__(self):
        self._plotter = Plot2D()
        self._processor = SimulationProcessor()
        self._cpu_executor = support.AsyncExecutor(1)

        self._rendering = None
        self._simulation_daemon = None
        self._paused = None

        self._plotter.add_on_keyboard_callback(self._pause_cb)

    def start(self):
        self._rendering = support.wrap_exc(asyncio.ensure_future(self._plotter.render_loop()), logger)
        self._simulation_daemon = support.wrap_exc(asyncio.ensure_future(self._simulation()), logger)

    def _pause_cb(self, window, key, scancode, action, mods):
        if self._paused is None and (action == glfw.PRESS and key == glfw.KEY_SPACE):
            self._pause()

    def _pause(self):
        print("Paused! Press SPACE to continue...")
        self._paused = asyncio.Future()

        def cb(window, key, scancode, action, mods):
            if action == glfw.PRESS and key == glfw.KEY_SPACE:
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
        n = 100
        dx, dt, view_dt = 0.01, 0.1, 0.05
        iterations = 10
        u, chi = 0.0, 0.0025

        t_min, t_max = 0.0, 1.0
        ts = initial_generators.linear_peak_function(n, n // 2, t_min, t_max, t_min)
        # ts = initial_generators.step_function(n, n // 2)

        self._plotter.set_ys_range(t_min, t_max)
        self._plotter.set_ys(ts)
        self._pause()
        tics_limiter = FPSLimiter(1 / view_dt)

        while True:
            ts = yield from self._cpu_executor.map(self._processor.process, ts, dx=dx, dt=dt, u=u, chi=chi,
                                                   method_name='explicit_central', iters=iterations)
            self._plotter.set_ys(ts)
            if self._paused is not None:
                yield from self._paused
            yield from tics_limiter.ensure_frame_limit()
            # print('{:.1f} FPS'.format(tics_limiter.get_fps()))
