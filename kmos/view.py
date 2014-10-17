#!/usr/bin/env python
"""Run and view a kMC model. For this to work one needs a
kmc_model.(so/pyd) and a kmc_settings.py in the import path."""
#    Copyright 2009-2013 Max J. Hoffmann (mjhoffmann@gmail.com)
#    This file is part of kmos.
#
#    kmos is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    kmos is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with kmos.  If not, see <http://www.gnu.org/licenses/>.

import multiprocessing
import threading
import os

import numpy as np
import time


from ase.gui.images import Images
import ase

try:
    import gtk
    import gobject
    from ase.gui.view import View
    from ase.gui.status import Status
except Exception, e:
    View = type('View', (), {})
    Status = type('Status', (), {})
    print('Warning: GTK not available. Cannot run graphical front-end')
    print(e)

try:
    import matplotlib
    if os.name == 'posix':
        matplotlib.use('GTKAgg')
    elif os.name == 'nt':
        matplotlib.use('wxagg')
    else:
        matplotlib.use('GTKAgg')
    import matplotlib.pylab as plt
except Exception, e:
    print('Could not import matplotlib frontend for real-time plotting')
    print(e)


from kmos.run import KMC_Model, get_tof_names, lattice, settings


class ParamSlider(gtk.HScale):
    """A horizontal slider bar allowing the user to adjust a model parameter
    at runtime.
    """

    def __init__(self, name, value, xmin, xmax, scale, parameter_callback):
        self.parameter_callback = parameter_callback
        self.resolution = 1000.
        adjustment = gtk.Adjustment(0, 0, self.resolution, 0.1, 1.)
        self.xmin = float(xmin)
        self.xmax = float(xmax)
        if self.xmin == self.xmax:
            self.xmax = self.xmax + 1.
        self.settings = settings
        self.param_name = name
        self.scale = scale
        gtk.HScale.__init__(self, adjustment)
        self.connect('format-value', self.linlog_scale_format)
        self.connect('value-changed', self.value_changed)
        self.set_tooltip_text(self.param_name)
        if self.scale == 'linear':
            scaled_value = (self.resolution * (float(value) - self.xmin) /
                                               (self.xmax - self.xmin))
            self.set_value(scaled_value)
        elif self.scale == 'log':
            scaled_value = 1000 * (np.log(float(value) / self.xmin) /
                                   np.log(float(self.xmax / self.xmin)))
            self.set_value(scaled_value)

    def linlog_scale_format(self, _widget, value):
        """Format a model parameter's name for display above
        the slider bar.
        """
        value /= self.resolution
        name = self.param_name
        unit = ''
        if self.param_name.endswith('gas'):
            name = name[:-3]
        if self.param_name.startswith('p_'):
            name = 'p(%s)' % name[2:]
            unit = 'bar'
        if name == 'T':
            unit = 'K'
        if self.scale == 'log':
            vstr = '%s: %.2e %s (log)' % (name,
                           self.xmin * (self.xmax / self.xmin) ** value, unit)
        elif self.scale == 'linear':
            vstr = '%s: %s %s' % (name,
                           self.xmin + value * (self.xmax - self.xmin), unit)
        return vstr

    def value_changed(self, _widget):
        """Handle the event, that slider bar has been dragged."""
        scale_value = self.get_value() / self.resolution
        if self.scale == 'log':
            value = self.xmin * (self.xmax / self.xmin) ** scale_value
        else:
            value = self.xmin + (self.xmax - self.xmin) * scale_value
        self.parameter_callback(self.param_name, value)


class FakeWidget():
    """This widget is used by FakeUI containing the menu
    base settings that the ase.gui.images modules expects.
    """

    def __init__(self, path):
        self.active = False
        if path.endswith('ShowUnitCell'):
            self.active = True
        elif path.endswith('ShowBonds'):
            self.active = False
        elif path.endswith('ShowAxes'):
            self.active = True

    def get_active(self):
        return self.active


class FakeUI():
    """This is a fudge class to simulate to the View class a non-existing
    menu with included settings
    """

    def __init__(self):
        return self

    def get_widget(self, path):
        widget = FakeWidget(path)
        return widget


class KMC_ViewBox(threading.Thread, View, Status, FakeUI):
    """The part of the viewer GUI that displays the model's
    current configuration.
    """

    def __init__(self, queue, signal_queue, vbox, window,
                rotations='', show_unit_cell=True, show_bonds=False):

        threading.Thread.__init__(self)
        self.image_queue = queue
        self.signal_queue = signal_queue
        self.configured = False
        self.ui = FakeUI.__init__(self)
        self.images = Images()
        self.images.initialize([ase.atoms.Atoms()])
        self.killed = False
        self.paused = False

        self.vbox = vbox
        self.window = window

        self.vbox.connect('scroll-event', self.scroll_event)
        self.window.connect('key-press-event', self.on_key_press)
        View.__init__(self, self.vbox, rotations)
        Status.__init__(self, self.vbox)
        self.vbox.show()

        if os.name == 'posix':
            self.live_plot = True
        else:
            self.live_plot = False

        self.drawing_area.realize()
        self.scale = 10.0
        self.center = np.array([8, 8, 8])
        self.set_colors()
        self.set_coordinates(0)
        self.center = np.array([0, 0, 0])

        self.tofs = get_tof_names()

        # history tracking arrays
        self.times = []
        self.tof_hist = []
        self.occupation_hist = []

        # prepare diagrams
        self.data_plot = plt.figure()
        #plt.xlabel('$t$ in s')
        self.tof_diagram = self.data_plot.add_subplot(211)
        self.tof_diagram.set_yscale('log')
        #self.tof_diagram.get_yaxis().get_major_formatter().set_powerlimits(
                                                                    #(3, 3))
        self.tof_plots = []
        for tof in self.tofs:
            self.tof_plots.append(self.tof_diagram.plot([], [], label=tof)[0])

        self.tof_diagram.legend(loc='lower left')
        self.tof_diagram.set_ylabel(
            'TOF in $\mathrm{s}^{-1}\mathrm{site}^{-1}$')
        self.occupation_plots = []
        self.occupation_diagram = self.data_plot.add_subplot(212)
        for species in sorted(settings.representations):
            self.occupation_plots.append(
                self.occupation_diagram.plot([], [], label=species)[0],)
        self.occupation_diagram.legend(loc=2)
        self.occupation_diagram.set_xlabel('$t$ in s')
        self.occupation_diagram.set_ylabel('Coverage')

    def update_vbox(self, atoms):
        """Update the ViewBox."""
        if not self.center.any():
            self.center = atoms.cell.diagonal() * .5
        self.images = Images([atoms])
        self.images.filenames = ['kmos GUI - %s' % settings.model_name]
        self.set_colors()
        self.set_coordinates(0)
        self.draw()
        self.label.set_label('%.3e s (%.3e steps)' % (atoms.kmc_time,
                                                    atoms.kmc_step))

    def update_plots(self, atoms):
        """Update the coverage and TOF plots."""
        # fetch data piggy-backed on atoms object
        new_time = atoms.kmc_time

        occupations = atoms.occupation.sum(axis=1) / lattice.spuck
        tof_data = atoms.tof_data

        # store locally
        while len(self.times) > getattr(settings, 'hist_length', 30):
            self.tof_hist.pop(0)
            self.times.pop(0)
            self.occupation_hist.pop(0)

        self.times.append(atoms.kmc_time)
        self.tof_hist.append(tof_data)
        self.occupation_hist.append(occupations)

        # plot TOFs
        for i, tof_plot in enumerate(self.tof_plots):
            tof_plot.set_xdata(self.times)
            tof_plot.set_ydata([tof[i] for tof in self.tof_hist])
            self.tof_diagram.set_xlim(self.times[0], self.times[-1])
            self.tof_diagram.set_ylim(1e-3,
                      10 * max([tof[i] for tof in self.tof_hist]))

        # plot occupation
        for i, occupation_plot in enumerate(self.occupation_plots):
            occupation_plot.set_xdata(self.times)
            occupation_plot.set_ydata(
                            [occ[i] for occ in self.occupation_hist])
        self.occupation_diagram.set_xlim([self.times[0], self.times[-1]])

        self.data_plot.canvas.draw_idle()
        manager = plt.get_current_fig_manager()
        if hasattr(manager, 'toolbar'):
            toolbar = manager.toolbar
            if hasattr(toolbar, 'set_visible'):
                toolbar.set_visible(False)

        plt.show()

        # [:] is necessary so that it copies the
        # values and doesn't reinitialize the pointer
        self.time = new_time

        return False

    def kill(self):
        self.killed = True

    def run(self):
        time.sleep(1.)
        while not self.killed:
            time.sleep(0.05)
            if not self.image_queue.empty():
                atoms = self.image_queue.get()
                gobject.idle_add(self.update_vbox, atoms)
                if self.live_plot:
                    gobject.idle_add(self.update_plots, atoms)

    def on_key_press(self, _widget, event):
        """Process key press event on view box."""
        signal_dict = {'a': 'ACCUM_RATE_SUMMATION',
                       'c': 'COVERAGE',
                       'd': 'DOUBLE',
                       'h': 'HALVE',
                       's': 'SWITCH_SURFACE_PROCESSS_OFF',
                       'S': 'SWITCH_SURFACE_PROCESSS_ON',
                       'w': 'WRITEOUT',
                      }
        if event.string in [' ', 'p']:
            if not self.paused:
                self.signal_queue.put('PAUSE')
                self.paused = True
            else:
                self.signal_queue.put('START')
                self.paused = False
        elif event.string in ['?']:
            for key, command in signal_dict.items():
                print('%4s %s' % (key, command))
        elif event.string in signal_dict:
            self.signal_queue.put(signal_dict.get(event.string, ''))

    def scroll_event(self, _window, event):
        """Zoom in/out when using mouse wheel"""
        x = 1.0
        if event.direction == gtk.gdk.SCROLL_UP:
            x = 1.2
        elif event.direction == gtk.gdk.SCROLL_DOWN:
            x = 1.0 / 1.2
        self._do_zoom(x)

    def _do_zoom(self, x):
        """Utility method for zooming"""
        self.scale *= x
        try:
            atoms = self.image_queue.get()
        except Exception, e:
            atoms = ase.atoms.Atoms()
            print(e)
        self.update_vbox(atoms)


class KMC_ModelProxy(multiprocessing.Process):
    """This is a proxy class handling the communication
    with the Model process.

    This proxy was necessary because Windows does not
    support fork() and thus the model process cannot be split-off
    directly. As a workaround multiprocessing tries to pickle the
    memory of the current process, however it does not know how
    to pickle the fortran objects.
    """
    def __init__(self, *args, **kwargs):
        super(KMC_ModelProxy, self).__init__()
        self.steps_per_frame = kwargs.get('steps_per_frame', 50000)
        self.model = kwargs.get('model', None, )
        self.kwargs = kwargs
        self.signal_queue = self.kwargs.get('signal_queue')
        self.parameter_queue = self.kwargs.get('parameter_queue')
        self.queue = self.kwargs.get('queue')

    def run(self):
        if self.model is None:
            self.model = KMC_Model(self.queue,
                                   self.parameter_queue,
                                   self.signal_queue,
                                   steps_per_frame=self.steps_per_frame)
        self.model.run()

    def join(self):
        self.signal_queue.put('JOIN')
        super(KMC_ModelProxy, self).join()

    def terminate(self):
        self.signal_queue.put('STOP')
        super(KMC_ModelProxy, self).terminate()


class KMC_Viewer():
    """A graphical front-end to run, manipulate
    and view a kMC model.
    """

    def __init__(self, model=None, steps_per_frame=50000):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_position(gtk.WIN_POS_CENTER)
        self.window.connect('delete-event', self.exit)

        self.vbox = gtk.VBox()
        self.window.add(self.vbox)
        queue = multiprocessing.Queue(maxsize=3)
        self.parameter_queue = multiprocessing.Queue(maxsize=50)
        self.signal_queue = multiprocessing.Queue(maxsize=10)
        if model is None:
            self.model = KMC_ModelProxy(queue=queue,
                                        parameter_queue=self.parameter_queue,
                                        signal_queue=self.signal_queue,
                                        steps_per_frame=steps_per_frame)
        else:
            self.model = model
            self.model.image_queue = queue
            self.model.parameter_queue = self.parameter_queue
            self.model.signal_queue = self.signal_queue
        self.viewbox = KMC_ViewBox(queue, self.signal_queue,
                                   self.vbox, self.window)

        adjustable_params = [param for param in settings.parameters
                             if settings.parameters[param]['adjustable']]

        for param_name in sorted(adjustable_params):
            param = settings.parameters[param_name]
            slider = ParamSlider(param_name, param['value'],
                                 param['min'], param['max'],
                                 param['scale'], self.parameter_callback)
            self.vbox.add(slider)
            self.vbox.set_child_packing(slider, expand=False,
                                        fill=False, padding=0,
                                        pack_type=gtk.PACK_START)
        self.window.set_title('kmos GUI')
        self.window.show_all()

    def parameter_callback(self, name, value):
        """Sent (updated) parameters to the model process."""
        settings.parameters[name]['value'] = value
        self.parameter_queue.put(settings.parameters)

    def exit(self, _widget, _event):
        """Exit the viewer application cleanly
        killing all subprocesses before the main
        process.
        """

        self.viewbox.kill()
        #print(' ... sent kill to viewbox')
        self.viewbox.join()
        #print(' ... viewbox thread joined')
        self.signal_queue.put('STOP')
        #print(' ... sent stop to model')
        self.model.terminate()
        self.model.join()
        #print(' ... model thread joined')
        #base.deallocate_system()
        gtk.main_quit()
        return True


def main(model=None, steps_per_frame=50000):
    """The entry point for the kmos viewer application. In order to
    run and view a model the corresponding kmc_settings.py and
    kmc_model.(so/pyd) must be in the current import path, e.g. ::

        from sys import path
        path.append('/path/to/model')
        from kmos.view import main
        main() # launch viewer
    """

    gobject.threads_init()
    viewer = KMC_Viewer(model, steps_per_frame=steps_per_frame)
    viewer.model.start()
    viewer.viewbox.start()
    gtk.main()
