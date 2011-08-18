#!/usr/bin/env python

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
try:
    from kmc_model import base, lattice, proclist
except:
    print('Could not find the kmc module. The kmc implements the actual')
    print('kmc model. This can be created from a kmos xml file using')
    print('kmos-export-program.')
    raise
try:
    import kmc_settings as settings
except:
    print('Could not find the settings file')
    print('The kmos_settings.py contains all changeable model parameters')
    print('and descriptions for the representation on screen.')


class KMC_Model(multiprocessing.Process):
    def __init__(self, image_queue, parameter_queue, signal_queue, size=None, system_name='kmc_model'):
        super(KMC_Model, self).__init__()
        self.image_queue = image_queue
        self.parameter_queue = parameter_queue
        self.signal_queue = signal_queue
        self.size = int(settings.simulation_size) if size is None else int(size)
        proclist.init((self.size,)*int(lattice.model_dimension),
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
                atoms.size = self.size
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
                elif signal.upper() == 'RESET_TIME':
                    base.set_kmc_time(0.0)
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
        print('-------------------')

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
        print('%s %s %s %s' % (name, value, min, max))
        self.parameter_callback = parameter_callback
        self.resolution = 1000.
        adjustment = gtk.Adjustment(0, 0, self.resolution, 0.1, 1.)
        self.xmin = float(min)
        self.xmax = float(max)
        self.settings = settings
        self.param_name = name
        self.scale = scale
        gtk.HScale.__init__(self, adjustment)
        self.connect('format-value', self.linlog_scale_format)
        self.connect('value-changed',self.value_changed)
        self.set_tooltip_text(self.param_name)
        self.set_value((self.resolution*(float(value)-self.xmin)/(self.xmax-self.xmin)))
        print('set value %s' % self.get_value())

    def linlog_scale_format(self, widget, value):
        value /= self.resolution
        name = self.param_name
        unit = ''
        if self.param_name.endswith('gas'):
            name = name[:-3]
        if self.param_name.startswith('p_'):
            name = name[2 :]
            unit = 'bar'
        if name == 'T':
            unit = 'K'
        if self.scale == 'log':
            vstr =  '%s: %.2e %s' % (name, self.xmin*(self.xmax/self.xmin)**value, unit)
        else:
            vstr = '%s: %s %s' % (name, self.xmin+value*(self.xmax-self.xmin), unit)
        return vstr

    def value_changed(self, widget):
        scale_value = self.get_value()/self.resolution
        if self.scale == 'log':
            value = self.xmin*(self.xmax/self.xmin)**scale_value
        else:
            value = self.xmin +  (self.xmax-self.xmin)*scale_value
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
    def __init__(self, queue, signal_queue, vbox, window, rotations='', show_unit_cell=True, show_bonds=False):
        threading.Thread.__init__(self)
        self.image_queue = queue
        self.signal_queue = signal_queue
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
                self.tof_matrix[tofs.index(tof), process_nr-1] += tof_factor

        # history tracking arrays
        self.times = []
        self.tof_hist = []
        self.occupation_hist = []

        # prepare procstat
        self.procstat = np.zeros((proclist.nr_of_proc,))
        self.time = 0.
        # prepare diagrams
        self.data_plot = plt.figure()
        #plt.xlabel('$t$ in s')
        self.tof_diagram = self.data_plot.add_subplot(211)
        self.tof_plots = []
        for tof in self.tofs:
            self.tof_plots.append(self.tof_diagram.plot([],[],'b-')[0])

        self.tof_diagram.set_ylabel('TOF in $\mathrm{s}^{-1}\mathrm{site}^{-1}$')
        self.occupation_plots =[]
        self.occupation_diagram = self.data_plot.add_subplot(212)
        for species in sorted(settings.representations):
            self.occupation_plots.append(self.occupation_diagram.plot([], [],label=species)[0],)
        self.occupation_diagram.legend(loc=2)
        self.occupation_diagram.set_xlabel('$t$ in s')
        self.occupation_diagram.set_ylabel('Coverage')

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
        # fetch data piggy-backed on atoms object
        new_time = atoms.kmc_time
        new_procstat = atoms.procstat
        delta_t = (new_time - self.time)
        size = atoms.size*lattice.model_dimension
        if delta_t == 0. :
            print("Warning: numerical precision too low, to resolve time-steps")
            print('         Will reset kMC for next step')
            self.signal_queue.put('RESET_TIME')
            return False
        tof_data = np.dot(self.tof_matrix,  (new_procstat - self.procstat)/delta_t/size)


        occupations = atoms.occupation.sum(axis=1)/lattice.spuck

        # store locally
        while len(self.times) > 30 :
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
        self.tof_diagram.set_xlim(self.times[0],self.times[-1])
        self.tof_diagram.set_ylim(0,max([tof[i] for tof in self.tof_hist]))

        # plot occupation
        for i, occupation_plot in enumerate(self.occupation_plots):
            self.occupation_plots[i].set_xdata(self.times)
            self.occupation_plots[i].set_ydata([occ[i] for occ in self.occupation_hist])
        self.occupation_diagram.set_xlim([self.times[0],self.times[-1]])

        self.data_plot.canvas.draw_idle()
        plt.show()

        # [:] is necessary so that it copies the
        # values and doesn't reinitialize the pointer
        self.time = new_time
        self.procstat[:] = new_procstat

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
        self.signal_queue = multiprocessing.Queue(maxsize=10)
        self.model = KMC_Model(queue, self.parameter_queue, self.signal_queue)
        self.viewbox = KMC_ViewBox(queue, self.signal_queue, self.vbox, self.window)

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
        self.signal_queue.put('STOP')
        print(' ... sent stop to model')
        self.model.terminate()
        self.model.join()
        print(' ... model thread joined')
        base.deallocate_system()
        gtk.main_quit()
        return True
