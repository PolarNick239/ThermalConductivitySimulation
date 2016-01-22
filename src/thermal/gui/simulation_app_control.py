#
# Copyright (c) 2015, Nikolay Polyarnyi
# All rights reserved.
#

import asyncio
import logging
import tkinter
from tkinter import messagebox

from thermal.utils.support import AsyncExecutor

logger = logging.getLogger(__name__)


class SimulationAppControl:

    def __init__(self,
                 *, initial_functions, methods, initial_function=None, method=None,
                 title='SimulationAppControl',
                 **kwargs):
        self._int_param_names = ['n', 'iters']
        self._optional_float_param_names = ['r', 's']
        self._float_param_names = ['dx', 'dt', 'u', 'chi', 'view_dt']
        self._entries = {}

        self._master = tkinter.Tk(className=title)

        tkinter.Label(self._master, text="Initial value:").grid(row=0)
        self._initial_function_entry = tkinter.StringVar()
        if initial_function is not None:
            assert initial_function in initial_functions
            self._initial_function_entry.set(initial_function)
        init_drop_down = tkinter.OptionMenu(self._master, self._initial_function_entry, *initial_functions)
        init_drop_down.grid(row=0, column=1)

        tkinter.Label(self._master, text="Method name:").grid(row=1)
        self._method_entry = tkinter.StringVar()
        if method is not None:
            assert method in methods
            self._method_entry.set(method)
        method_drop_down = tkinter.OptionMenu(self._master, self._method_entry, *methods)
        method_drop_down.grid(row=1, column=1)

        tkinter.Label(self._master, text="Params:").grid(row=2)
        row_num = 3
        for name in self._int_param_names + self._float_param_names + self._optional_float_param_names:
            tkinter.Label(self._master, text="{}".format(name)).grid(row=row_num)
            self._entries[name] = tkinter.Entry(self._master)
            self._entries[name].grid(row=row_num, column=1)
            row_num += 1

        for name, value in kwargs.items():
            if value is None:
                value = ''
            self._entries[name].insert(0, str(value))
            assert name in self._int_param_names + self._float_param_names + self._optional_float_param_names

        self._ok_button = tkinter.Button(self._master, text='Restart', command=self._on_ok)
        self._ok_button.grid(row=row_num, column=1)
        self._on_ok_callbacks = set()

        row_num += 1
        tkinter.Label(self._master, text="Press SPACE on main window to (un)pause").grid(row=row_num, columnspan=2)

    def get_initial_function_name(self):
        return self._initial_function_entry.get()

    def get_method_name(self):
        return self._method_entry.get()

    def get_params_values(self):
        values = {}
        for param_name in self._int_param_names:
            try:
                values[param_name] = int(self._entries[param_name].get())
            except ValueError:
                logger.warn('Incorrect input in int {}!'.format(param_name))
                tkinter.messagebox.showwarning('Incorrect input', message='{} should be integer!'.format(param_name))
                self._entries[param_name].selection_from(0)
                self._entries[param_name].selection_to(tkinter.END)
                return None
        for param_name in self._float_param_names:
            try:
                values[param_name] = float(self._entries[param_name].get())
            except ValueError:
                logger.warn('Incorrect input in float {}!'.format(param_name))
                tkinter.messagebox.showwarning('Incorrect input', message='{} should be float!'.format(param_name))
                self._entries[param_name].selection_from(0)
                self._entries[param_name].selection_to(tkinter.END)
                return None
        for param_name in self._optional_float_param_names:
            try:
                value = self._entries[param_name].get()
                if len(value) == 0:
                    values[param_name] = None
                else:
                    values[param_name] = float(value)
            except ValueError:
                logger.warn('Incorrect input in float {}!'.format(param_name))
                tkinter.messagebox.showwarning('Incorrect input', message='{} should be float or empty!'.format(param_name))
                self._entries[param_name].selection_from(0)
                self._entries[param_name].selection_to(tkinter.END)
                return None
        return values

    def _on_ok(self):
        init_func_name = self.get_initial_function_name()
        method_name = self.get_method_name()
        values = self.get_params_values()

        if values is None:
            return

        for cb in self._on_ok_callbacks:
            cb(init_func_name, method_name, values)

    def add_on_ok(self, cb):
        self._on_ok_callbacks.add(cb)

    def add_on_close(self, cb):
        self._master.protocol("WM_DELETE_WINDOW", cb)

    def run_loop(self):
        self._master.mainloop()

    def stop_loop(self):
        self._master.destroy()


@asyncio.coroutine
def _main():
    from thermal.simulation.processor import SimulationProcessor
    from thermal.simulation.initial_generators import list_functions

    processor = SimulationProcessor()

    gui_executor = AsyncExecutor(1)
    gui = yield from gui_executor.map(SimulationAppControl,
                                      initial_functions=list_functions(), methods=processor.get_method_names(),
                                      initial_function='linear_peak_function', method='explicit_central',
                                      n=100)
    gui.add_on_ok(lambda: print("Ok! Values: {}".format(gui.get_params_values())))
    yield from gui_executor.map(gui.run_loop)


if __name__ == '__main__':
    asyncio.get_event_loop().run_until_complete(_main())
