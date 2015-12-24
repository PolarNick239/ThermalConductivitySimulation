#
# Copyright (c) 2015, Nikolay Polyarnyi
# All rights reserved.
#

import asyncio
import functools

from thermal.gui.simulation_app import SimulationApp
from thermal.simulation.processor import SimulationProcessor
from thermal.simulation.initial_generators import list_functions
from thermal.gui.simulation_app_control import SimulationAppControl
from thermal.utils import support
from thermal.utils.support import AsyncExecutor


@asyncio.coroutine
def _main():
    initial_function = 'step_function'
    method = 'explicit_central'
    params = dict(n=100, iters=10,
                  dx=0.01, dt=0.1, u=0.0, chi=0.0025,
                  view_dt=0.05)

    processor = SimulationProcessor()
    simulation = SimulationApp(processor)

    gui_executor = AsyncExecutor(1)
    control = yield from gui_executor.map(SimulationAppControl,
                                          initial_functions=list_functions(), methods=processor.get_method_names(),
                                          initial_function=initial_function, method=method,
                                          **params)

    restart_tasks = asyncio.Queue()

    @asyncio.coroutine
    def restart_loop():
        while True:
            init_func_name, method_name, values = yield from restart_tasks.get()
            print("Restart!")
            simulation.setup(init_func_name, method_name, values)
    restart_daemon = support.wrap_exc(asyncio.ensure_future(restart_loop()))

    control.add_on_ok(lambda init_func_name, method_name, values:
                      restart_tasks.put_nowait((init_func_name, method_name, values)))

    simulation.setup(initial_function, method, params)
    simulation.start()

    exited = asyncio.Future()
    yield from gui_executor.map(control.add_on_close, functools.partial(exited.set_result, True))
    yield from gui_executor.map(control.run_loop)
    yield from exited

    simulation.stop()
    restart_daemon.cancel()
    yield from gui_executor.map(control.stop_loop)

if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(_main())
