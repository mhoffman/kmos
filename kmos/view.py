#!/usr/bin/env python
"""Run and view a kMC model. For this to work one needs a
kmc_model.so and a kmc_settings.py in the import path."""
#    Copyright 2009-2012 Max J. Hoffmann (mjhoffmann@gmail.com)
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

import numpy as np
import math
import time
from copy import deepcopy


import ase.gui.ag
from ase.atoms import Atoms
from ase.gui.images import Images
#from ase.gui.defaults import read_defaults



try:
    import matplotlib
    matplotlib.use('GTKAgg')
    import matplotlib.pylab as plt
except:
    print('Could not import matplotlib frontend. Needed for real-time plotting')

try:
    import gtk
    import gobject
    from ase.gui.view import View
    from ase.gui.status import Status
except:
    print('Warning: GTK not available. Cannot run graphical front-end')


from kmos import species, units, evaluate_rate_expression
from kmos.run import KMC_Model,\
                       base,\
                       get_tof_names,\
                       lattice,\
                       proclist,\
                       settings


class ParamSlider(gtk.HScale):
    def __init__(self, name, value, min, max, scale, parameter_callback):
        #print('%s %s %s %s' % (name, value, min, max))
        self.parameter_callback = parameter_callback
        self.resolution = 1000.
        adjustment = gtk.Adjustment(0, 0, self.resolution, 0.1, 1.)
        self.xmin = float(min)
        self.xmax = float(max)
        if self.xmin == self.xmax :
            self.xmax = self.xmax + 1.
        self.settings = settings
        self.param_name = name
        self.scale = scale
        gtk.HScale.__init__(self, adjustment)
        self.connect('format-value', self.linlog_scale_format)
        self.connect('value-changed', self.value_changed)
        self.set_tooltip_text(self.param_name)
        if self.scale == 'linear':
            scaled_value = (self.resolution * ( float(value) - self.xmin) / (self.xmax - self.xmin))
            self.set_value(scaled_value)
        elif self.scale == 'log':
            scaled_value = 1000*(np.log(float(value)/self.xmin)/np.log(float(self.xmax/self.xmin)))
            self.set_value(scaled_value)

    def linlog_scale_format(self, widget, value):
        value /= self.resolution
        name = self.param_name
        unit = ''
        if self.param_name.endswith('gas'):
            name = name[:-3]
        if self.param_name.startswith('p_'):
            name = name[2:]
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

    def value_changed(self, widget):
        scale_value = self.get_value() / self.resolution
        if self.scale == 'log':
            value = self.xmin * (self.xmax / self.xmin) ** scale_value
        else:
            value = self.xmin + (self.xmax - self.xmin) * scale_value
        self.parameter_callback(self.param_name, value)


class FakeWidget():
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

        #print('initialized viewbox')

    def update_vbox(self, atoms):
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
        # fetch data piggy-backed on atoms object
        new_time = atoms.kmc_time
        new_procstat = atoms.procstat

        occupations = atoms.occupation.sum(axis=1) / lattice.spuck
        tof_data = atoms.tof_data

        # store locally
        while len(self.times) > 30:
            self.tof_hist.pop(0)
            self.times.pop(0)
            self.occupation_hist.pop(0)

        self.times.append(atoms.kmc_time)
        self.tof_hist.append(tof_data)
        self.occupation_hist.append(occupations)

        # plot TOFs
        for i, tof_plot in enumerate(self.tof_plots):
            self.tof_plots[i].set_xdata(self.times)
            self.tof_plots[i].set_ydata([tof[i] for tof in self.tof_hist])
            self.tof_diagram.set_xlim(self.times[0], self.times[-1])
            self.tof_diagram.set_ylim(1e-3,
                      max([tof[i] for tof in self.tof_hist]))

        # plot occupation
        for i, occupation_plot in enumerate(self.occupation_plots):
            self.occupation_plots[i].set_xdata(self.times)
            self.occupation_plots[i].set_ydata(
                            [occ[i] for occ in self.occupation_hist])
        self.occupation_diagram.set_xlim([self.times[0], self.times[-1]])

        self.data_plot.canvas.draw_idle()
        manager = plt.get_current_fig_manager()
        toolbar = manager.toolbar
        toolbar.set_visible(False)

        plt.show()

        # [:] is necessary so that it copies the
        # values and doesn't reinitialize the pointer
        self.time = new_time

        return False

    def kill(self):
        self.killed = True
        #print('  ... viewbox received kill')

    def run(self):
        time.sleep(1.)
        while not self.killed:
            time.sleep(0.05)
            if not self.image_queue.empty():
                atoms = self.image_queue.get()
                gobject.idle_add(self.update_vbox, atoms)
                gobject.idle_add(self.update_plots, atoms)

    def on_key_press(self, window, event):
        if event.string in [' ', 'p']:
            if not self.paused:
                self.signal_queue.put('PAUSE')
                self.paused = True
            else:
                self.signal_queue.put('START')
                self.paused = False
        elif event.string == 'd':
            self.signal_queue.put('DOUBLE')
        elif event.string == 'h':
            self.signal_queue.put('HALVE')

    def scroll_event(self, window, event):
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


class KMC_Viewer():
    """A graphical front-end to run, manipulate
    and view a kMC model.
    """
    def __init__(self, model=None):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_position(gtk.WIN_POS_CENTER)
        self.window.connect('delete-event', self.exit)

        self.vbox = gtk.VBox()
        self.window.add(self.vbox)
        queue = multiprocessing.Queue(maxsize=3)
        self.parameter_queue = multiprocessing.Queue(maxsize=50)
        self.signal_queue = multiprocessing.Queue(maxsize=10)
        if model is None:
            self.model = KMC_Model(queue, self.parameter_queue, self.signal_queue)
        else:
            self.model = model
            self.model.image_queue = queue
            self.model.parameter_queue = self.parameter_queue
            self.model.signal_queue = self.signal_queue
        self.viewbox = KMC_ViewBox(queue, self.signal_queue,
                                   self.vbox, self.window)

        for param_name in filter(lambda p: \
            settings.parameters[p]['adjustable'], settings.parameters):
            param = settings.parameters[param_name]
            slider = ParamSlider(param_name, param['value'],
                                 param['min'], param['max'],
                                 param['scale'], self.parameter_callback)
            self.vbox.add(slider)
            self.vbox.set_child_packing(slider, expand=False,
                                        fill=False, padding=0,
                                        pack_type=gtk.PACK_START)
        #print('initialized kmc_viewer')
        #print(self.window.get_title())
        self.window.set_title('kmos GUI')
        #print(self.window.get_title())
        self.window.show_all()

    def parameter_callback(self, name, value):
        settings.parameters[name]['value'] = value
        self.parameter_queue.put(settings.parameters)

    def exit(self, widget, event):
        #print('Starting shutdown procedure')
        self.viewbox.kill()
        #print(' ... sent kill to viewbox')
        self.viewbox.join()
        #print(' ... viewbox thread joined')
        self.signal_queue.put('STOP')
        #print(' ... sent stop to model')
        self.model.terminate()
        self.model.join()
        #print(' ... model thread joined')
        base.deallocate_system()
        gtk.main_quit()
        return True



def main(model=None):
    from kmos.view import KMC_Viewer
    import gtk
    import gobject
    gobject.threads_init()
    viewer = KMC_Viewer(model)
    viewer.model.start()
    viewer.viewbox.start()
    #print('started model and viewbox processes')
    gtk.main()
    #print('gtk.main stopped')
