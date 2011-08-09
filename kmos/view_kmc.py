#!/usr/bin/python

import multiprocessing
import threading

import gtk
import gobject
import numpy as np
import math
import time
from copy import deepcopy


import ase.gui.ag
from ase.atoms import Atoms
from ase.gui.view import View
from ase.gui.images import Images
from ase.gui.status import Status
from ase.gui.defaults import read_defaults

import matplotlib
matplotlib.use('GTKAgg')
import matplotlib.pylab as plt


from kmos import species, units, evaluate_rate_expression
from kmc import base, lattice, proclist
import settings


class KMC_Model(multiprocessing.Process):
    def __init__(self, image_queue, parameter_queue, signal_queue, size=30, system_name='kmc_model'):
        super(KMC_Model, self).__init__()
        self.image_queue = image_queue
        self.parameter_queue = parameter_queue
        self.signal_queue = signal_queue
        proclist.init((size,)*int(lattice.model_dimension),
            system_name,
            lattice.default_layer,
            proclist.default_species)
        self.cell_size = np.dot(lattice.unit_cell_size, lattice.system_size)
        self.species_representation = []
        for species in sorted(settings.representations):
            if settings.representations[species].strip():
                self.species_representation.append(eval(settings.representations[species]))
            else:
                self.species_representation.append(Atoms())

        if len(settings.lattice_representation):
            self.lattice_representation = eval(settings.lattice_representation)[0]
        else:
            self.lattice_representation = Atoms()
        self.set_rate_constants(settings.parameters)

    def run(self):
        while True:
            for _ in xrange(50000):
                proclist.do_kmc_step()
            if not self.image_queue.full():
                atoms = self.get_atoms()
                # attach other quantities need to plot
                # to the atoms object and let it travel
                # piggy-back through the queue
                atoms.kmc_time = base.get_kmc_time()
                atoms.procstat = np.zeros((proclist.nr_of_proc,))
                atoms.occupation = proclist.get_occupation()
                for i in range(proclist.nr_of_proc):
                    atoms.procstat[i] = base.get_procstat(i+1)
                self.image_queue.put(atoms)
            if not self.signal_queue.empty():
                signal = self.signal_queue.get()
                print('  ... model received %s' % signal)
                if signal.upper() == 'STOP':
                    self.terminate()
                elif signal.upper() == 'PAUSE':
                    while self.signal_queue.empty():
                        time.sleep('0.03')
                elif signal.upper() == 'START':
                    pass
            if not self.parameter_queue.empty():
                while not self.parameter_queue.empty():
                    parameters = self.parameter_queue.get()
                self.set_rate_constants(parameters)


    def set_rate_constants(self, parameters):
        """Tries to evaluate the supplied expression for a rate constant
        to a simple real number and sets it for the corresponding process.
        For the evaluation we draw on predefined natural constants, user defined
        parameters and mathematical functions
        """
        for proc in sorted(settings.rate_constants):
            rate_expr = settings.rate_constants[proc][0]
            rate_const = evaluate_rate_expression(rate_expr, parameters)

            try:
                base.set_rate_const(eval('proclist.%s' % proc.lower()), rate_const)
                print('%s: %.3e s^{-1}' % (proc, rate_const))
            except Exception as e:
                raise UserWarning("Could not set %s for process %s!\nException: %s" % (rate_expr, proc, e))

    def get_atoms(self):
        atoms = ase.atoms.Atoms()
        atoms.set_cell(self.cell_size)
        atoms.kmc_time = base.get_kmc_time()
        atoms.kmc_step = base.get_kmc_step()
        for i in xrange(lattice.system_size[0]):
            for j in xrange(lattice.system_size[1]):
                for k in xrange(lattice.system_size[2]):
                    for n in xrange(1,1+lattice.spuck):
                        species = lattice.get_species([i,j,k,n])
                        if self.species_representation[species]:
                            atom = deepcopy(self.species_representation[species])
                            atom.translate(np.dot(lattice.unit_cell_size,
                            np.array([i,j,k]) + lattice.site_positions[n-1]))
                            atoms += atom
                    lattice_repr = deepcopy(self.lattice_representation)
                    lattice_repr.translate(np.dot(lattice.unit_cell_size,
                                np.array([i,j,k])))
                    atoms += lattice_repr

        return atoms
class ParamSlider(gtk.HScale):
    def __init__(self, name, value, min, max, scale, parameter_callback):
        self.settings = settings
        self.param_name = name
        self.value = float(value)
        self.scale = scale
        self.min = 0.
        self.max = 1.
        self.xmin = float(min)
        self.xmax = float(max)
        self.parameter_callback = parameter_callback
        adjustment = gtk.Adjustment(value=self.value, lower=self.min, upper=self.max)
        gtk.HScale.__init__(self, adjustment)
        self.connect('format-value', self.linlog_scale_format)
        self.connect('value-changed',self.value_changed)
        self.set_tooltip_text(self.param_name)
        adjustment.set_step_increment(0.01)

    def linlog_scale_format(self, widget, value):
        if self.scale == 'log':
            vstr =  '%.2e' % (self.xmin*(self.xmax/self.xmin)**value)
        else:
            vstr = '%s' % (self.xmin+value*(self.xmax-self.xmin))
        return vstr

    def value_changed(self, widget):
        if self.scale == 'log':
            value = self.xmin*(self.xmax/self.xmin)**self.get_value()
        else:
            value = self.xmin +  (self.xmax-self.xmin)*float(self.get_value())

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
    def __init__(self, queue, vbox, window, rotations='', show_unit_cell=True, show_bonds=False):
        threading.Thread.__init__(self)
        self.image_queue = queue
        self.configured = False
        self.ui = FakeUI.__init__(self)
        self.images = Images()
        self.images.initialize([ase.atoms.Atoms()])
        self.killed = False

        self.vbox = vbox
        self.window = window

        self.vbox.connect('scroll-event',self.scroll_event)
        View.__init__(self, self.vbox, rotations)
        Status.__init__(self, self.vbox)
        self.vbox.show()

        self.drawing_area.realize()
        self.scale = 10.0
        self.center = np.array([8, 8, 8])
        self.set_colors()
        self.set_coordinates(0)
        self.center = np.array([0,0,0])

        # prepare TOF counter
        tofs = []
        for process, tof_count in settings.tof_count.iteritems():
            for tof in tof_count:
                if tof not in tofs:
                    tofs.append(tof)
        self.tofs = tofs
        self.tof_matrix = np.zeros((len(tofs),proclist.nr_of_proc))
        for process, tof_count in settings.tof_count.iteritems():
            process_nr = eval('proclist.%s' % process.lower())
            for tof, tof_factor in tof_count.iteritems():
                print(tof, tof_factor)
                self.tof_matrix[tofs.index(tof), process_nr-1] += tof_factor

        # history tracking arrays
        self.times = []
        self.tof_hist = []
        self.occupation_hist = []

        # prepare procstat
        self.procstat = np.zeros((proclist.nr_of_proc,))
        # prepare diagrams
        self.data_plot = plt.figure()
        #plt.xlabel('$t$ in s')
        self.tof_diagram = self.data_plot.add_subplot(211)
        self.tof_plots = []
        for tof in self.tofs:
            self.tof_plots.append(self.tof_diagram.plot([],[],'b-')[0])
        self.occupation_plots =[]
        self.occupation_diagram = self.data_plot.add_subplot(212)
        for species in range(proclist.nr_of_species):
            self.occupation_plots.append(self.occupation_diagram.plot([], [],)[0])

        print('initialized viewbox')

    def update_vbox(self, atoms):
        if not self.center.any():
            self.center = atoms.cell.diagonal()*.5
        self.images = Images([atoms])
        self.images.filenames = ['kmos GUI - %s' % settings.model_name]
        self.set_colors()
        self.set_coordinates(0)
        self.draw()
        self.label.set_label('%.3e s (%.3e steps)' % (atoms.kmc_time,
                                                    atoms.kmc_step))

    def update_plots(self, atoms):
        # Determine turn-over-frequencies
        new_time = atoms.kmc_time
        new_procstat = atoms.procstat
        tof_data = np.dot(self.tof_matrix,  (new_procstat - self.procstat))
        # plot TOFs
        while len(self.tof_hist) > 100 :
            self.tof_hist.pop()
            self.times.pop()
        self.tof_hist.append(tof_data)
        self.times.append(atoms.kmc_time)
        for i, tof_plot in enumerate(self.tof_plots):
            self.tof_plots[i].set_xdata(self.times)
            self.tof_plots[i].set_ydata([tof[i] for tof in self.tof_hist])
        self.tof_diagram.set_xlim(self.times[0],self.times[-1])
        self.tof_diagram.set_ylim(0,max([tof[i] for tof in self.tof_hist]))
        self.occupation_diagram.set_xlim([self.times[0],self.times[-1]])

        # plot occupations
        while len(self.occupation_hist) > 100 :
            self.occupation_hist.pop()
        occupations = atoms.occupation.sum(axis=1)/lattice.spuck
        self.occupation_hist = [occupations] + self.occupation_hist
        #self.model.occupation_hist = [[random() for x in range(proclist.nr_of_species)]] + self.model.occupation_hist
        for i, occupation_plot in enumerate(self.occupation_plots):
            self.occupation_plots[i].set_xdata(self.times)
            self.occupation_plots[i].set_ydata([occ[i] for occ in self.occupation_hist])

        self.data_plot.canvas.draw_idle()
        plt.show()

        self.procstat[:] = new_procstat
        self.time = new_time

        return False

    def kill(self):
        self.killed = True
        print('  ... viewbox received kill')

    def run(self):
        time.sleep(1.)
        while not self.killed:
            time.sleep(0.05)
            if not self.image_queue.empty():
                atoms = self.image_queue.get()
                gobject.idle_add(self.update_vbox,atoms)
                gobject.idle_add(self.update_plots, atoms)

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
    def __init__(self):
        self.window = gtk.Window(gtk.WINDOW_TOPLEVEL)
        self.window.set_position(gtk.WIN_POS_CENTER)
        self.window.connect('delete-event',self.exit)

        self.vbox = gtk.VBox()
        self.window.add(self.vbox)
        queue = multiprocessing.Queue(maxsize=3)
        self.parameter_queue = multiprocessing.Queue(maxsize=50)
        self.model_rc = multiprocessing.Queue(maxsize=10)
        self.model = KMC_Model(queue, self.parameter_queue, self.model_rc)
        self.viewbox = KMC_ViewBox(queue, self.vbox, self.window)

        for param_name in filter(lambda p: settings.parameters[p]['adjustable'], settings.parameters):
            param = settings.parameters[param_name]
            slider = ParamSlider(param_name, param['value'], param['min'], param['max'], param['scale'], self.parameter_callback)
            self.vbox.add(slider)
            self.vbox.set_child_packing(slider, expand=False, fill=False, padding=0, pack_type=gtk.PACK_START)
        print('initialized kmc_viewer')
        print(self.window.get_title())
        self.window.set_title('kmos GUI')
        print(self.window.get_title())
        self.window.show_all()

    def parameter_callback(self, name, value):
        settings.parameters[name]['value'] = value
        self.parameter_queue.put(settings.parameters)

    def exit(self, widget, event):
        print('Starting shutdown procedure')
        self.viewbox.kill()
        print(' ... sent kill to viewbox')
        self.viewbox.join()
        print(' ... viewbox thread joined')
        self.model_rc.put('STOP')
        print(' ... sent stop to model')
        self.model.terminate()
        self.model.join()
        print(' ... model thread joined')
        base.deallocate_system()
        gtk.main_quit()
        return True


if __name__ == '__main__':
    gobject.threads_init()
    viewer = KMC_Viewer()
    viewer.model.start()
    viewer.viewbox.start()
    print('started model and viewbox processes')
    gtk.main()
    print('gtk.main stopped')
