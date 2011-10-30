#!/usr/bin/env python
"""
A python representation of a kMC model. The actual model is
imported in kmc_model.so and all parameters are stored in kmc_settings.py.

The model can be used directly like so::

    from kmos.model import KMC_Model
    model = KMC_Model()

    model.parameters.T = 500
    model.do_steps(100000)
    model.view()

which, of course can also be part of a python script.

The model also be run in a different process using the
multiprocessing module. This mode is designed for use with
a GUI so that the CPU intensive kMC integration can run at
full throttle without impeding the front-end. Interaction with
the model happens through Queues.
"""

#    Copyright 2009-2011 Max J. Hoffmann (mjhoffmann@gmail.com)
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

from copy import deepcopy
import multiprocessing
from math import log
import numpy as np
from ase.atoms import Atoms
from kmos import evaluate_rate_expression
try:
    from kmc_model import base, lattice, proclist
except Exception, e:
    print(e)
    print('Could not find the kmc module. The kmc implements the actual')
    print('kmc model. This can be created from a kmos xml file using')
    print('kmos-export-program.')
    base = lattice = proclist = None

try:
    import kmc_settings as settings
except Exception, e:
    print(e)
    print('Could import settings file')
    print('The kmc_settings.py contains all changeable model parameters')
    print('and descriptions for the representation on screen.')
    settings = None


class KMC_Model(multiprocessing.Process):
    """Front end to initialize and run kMC model using python bindings."""
    def __init__(self, image_queue=None,
                       parameter_queue=None,
                       signal_queue=None,
                       size=None, system_name='kmc_model',
                       banner=True,
                       print_rates=True):
        super(KMC_Model, self).__init__()
        self.image_queue = image_queue
        self.parameters_queue = parameter_queue
        self.signal_queue = signal_queue
        self.size = int(settings.simulation_size) \
                        if size is None else int(size)
        self.print_rates = print_rates
        self.parameters = Model_Parameters(self.print_rates)
        self.rate_constants = Model_Rate_Constants()
        proclist.init((self.size,) * int(lattice.model_dimension),
            system_name,
            lattice.default_layer,
            proclist.default_species,
            not banner)
        self.cell_size = np.dot(lattice.unit_cell_size, lattice.system_size)

        # prepare structures for TOF evaluation
        self.tofs = tofs = get_tof_names()
        self.tof_matrix = np.zeros((len(tofs), proclist.nr_of_proc))
        for process, tof_count in settings.tof_count.iteritems():
            process_nr = eval('proclist.%s' % process.lower())
            for tof, tof_factor in tof_count.iteritems():
                self.tof_matrix[tofs.index(tof), process_nr - 1] += tof_factor

        # prepare procstat
        self.procstat = np.zeros((proclist.nr_of_proc,))
        self.time = 0.

        self.species_representation = []
        for species in sorted(settings.representations):
            if settings.representations[species].strip():
                self.species_representation.append(
                    eval(settings.representations[species]))
            else:
                self.species_representation.append(Atoms())

        if len(settings.lattice_representation):
            self.lattice_representation = eval(
                settings.lattice_representation)[
                    lattice.substrate_layer]
        else:
            self.lattice_representation = Atoms()
        set_rate_constants(settings.parameters, self.print_rates)

    def __repr__(self):
        """Print short summary of current parameters and rate
        constants. It is advisable to include this at the beginning
        of every generated data file for later reconstruction
        """
        return (repr(self.parameters) + repr(self.rate_constants))

    def get_occupation_header(self):
        """Returns the names of the fields returned by
        self.get_atoms().occupation.
        """
        return ' '.join(['%s_%s' % (species, site)
                           for species in sorted(settings.representations)
                           for site in settings.site_names])

    def get_tof_header(self):
        """Returns the names of the fields returned by
        self.get_atoms().tof_data.
        """
        tofs = []
        for _, value in settings.tof_count.iteritems():
            for name in value:
                if name not in tofs:
                    tofs.append(name)
        return ' '.join(tofs)

    def deallocate(self):
        """Deallocate all arrays that are allocated
        by the Fortran module. This needs to be called
        whenever more than one simulation is started
        from one process.

        Note that the currenty state and history of
        the system is lost after calling this method.

        Note: explicit invocation was chosen over the
        __del__ method because there seems to easy
        portable way to control garbage collection.
        """

        lattice.deallocate_system()

    def do_steps(self, n=10000):
        """Propagate the model `n` steps."""
        for _ in xrange(n):
            proclist.do_kmc_step()

    def run(self):
        """Runs the model indefinitely. To control the
        simulations, model must have been initialized
        with proper Queues."""
        while True:
            for _ in xrange(500):
                proclist.do_kmc_step()
            if not self.image_queue.full():
                atoms = self.get_atoms()
                # attach other quantities need to plot
                # to the atoms object and let it travel
                # piggy-back through the queue
                atoms.size = self.size
                self.image_queue.put(atoms)
            if not self.signal_queue.empty():
                signal = self.signal_queue.get()
                print('  ... model received %s' % signal)
                if signal.upper() == 'STOP':
                    self.terminate()
                elif signal.upper() == 'PAUSE':
                    while self.signal_queue.empty():
                        time.sleep(0.03)
                elif signal.upper() == 'RESET_TIME':
                    base.set_kmc_time(0.0)
                elif signal.upper() == 'START':
                    pass
            if not self.parameters_queue.empty():
                while not self.parameters_queue.empty():
                    parameters = self.parameters_queue.get()
                set_rate_constants(parameters, self.print_rates)

    def view(self):
        """Visualize the current configuration of the model using ASE ag."""
        ase = import_ase()
        ase.visualize.view(self.get_atoms())

    def get_atoms(self):
        """Return an ASE Atoms object with additional 
        information such as coverage and Turn-over-frequencies
        attached."""
        ase = import_ase()
        atoms = ase.atoms.Atoms()
        atoms.calc = None
        atoms.set_cell(self.cell_size)
        atoms.kmc_time = base.get_kmc_time()
        atoms.kmc_step = base.get_kmc_step()
        for i in xrange(lattice.system_size[0]):
            for j in xrange(lattice.system_size[1]):
                for k in xrange(lattice.system_size[2]):
                    for n in xrange(1, 1 + lattice.spuck):
                        species = lattice.get_species([i, j, k, n])
                        if self.species_representation[species]:
                            atom = deepcopy(
                                self.species_representation[species])
                            atom.translate(np.dot(lattice.unit_cell_size,
                            np.array([i, j, k]) \
                            + lattice.site_positions[n - 1]))
                            atoms += atom
                    lattice_repr = deepcopy(self.lattice_representation)
                    lattice_repr.translate(np.dot(lattice.unit_cell_size,
                                np.array([i, j, k])))
                    atoms += lattice_repr

        # calculate TOF since last call
        atoms.procstat = np.zeros((proclist.nr_of_proc,))
        atoms.occupation = proclist.get_occupation()
        for i in range(proclist.nr_of_proc):
            atoms.procstat[i] = base.get_procstat(i + 1)
        delta_t = (atoms.kmc_time - self.time)
        size = self.size ** lattice.model_dimension
        if delta_t == 0. and atoms.kmc_time > 0:
            print(
                "Warning: numerical precision too low, to resolve time-steps")
            print('         Will reset kMC for next step')
            base.set_kmc_time(0.0)
            atoms.tof_data = np.zeros_like(self.tof_matrix[:, 0])
        else:
            atoms.tof_data = np.dot(self.tof_matrix,
                            (atoms.procstat - self.procstat) / delta_t / size)

        # update trackers for next call
        self.procstat[:] = atoms.procstat
        self.time = atoms.kmc_time

        return atoms


class Model_Parameters(object):
    def __init__(self, print_rates=True):
        object.__init__(self)
        self.__dict__.update(settings.parameters)
        self.print_rates = print_rates

    def __setattr__(self, attr, value):
        if attr in settings.parameters:
            settings.parameters[attr]['value'] = value
            set_rate_constants(print_rates=self.print_rates)
        else:
            self.__dict__[attr] = value

    def __repr__(self):
        res = '# kMC model parameters\n'
        res += '# --------------------\n'
        for attr in sorted(settings.parameters):
            res += ('# %s = %s\n' % (attr, settings.parameters[attr]['value']))
        res += '# --------------------\n'
        return res


class Model_Rate_Constants(object):
    def __repr__(self):
        res = '# kMC rate constants\n'
        res += '# ------------------\n'
        for proc in sorted(settings.rate_constants):
            rate_expr = settings.rate_constants[proc][0]
            rate_const = evaluate_rate_expression(rate_expr,
                                                  settings.parameters)
            res += '# %s: %s = %.2e s^{-1}\n' % (proc, rate_expr, rate_const)
        res += '# ------------------\n'
        return res


def set_rate_constants(parameters=None, print_rates=True):
    """Tries to evaluate the supplied expression for a rate constant
    to a simple real number and sets it for the corresponding process.
    For the evaluation we draw on predefined natural constants, user defined
    parameters and mathematical functions
    """
    if parameters is None:
        parameters = settings.parameters

    if print_rates:
        print('-------------------')
    for proc in sorted(settings.rate_constants):
        rate_expr = settings.rate_constants[proc][0]
        rate_const = evaluate_rate_expression(rate_expr, parameters)

        try:
            base.set_rate_const(eval('proclist.%s' % proc.lower()), rate_const)
            if print_rates:
                n = int(4*log(rate_const))
                print('%30s: %.3e s^{-1}: %s' % (proc, rate_const, '#'*n))
        except Exception as e:
            raise UserWarning(
                "Could not set %s for process %s!\nException: %s" \
                    % (rate_expr, proc, e))
    if print_rates:
        print('-------------------')


def import_ase():
    try:
        import ase
    except:
        print('Please download the ASE from')
        print('https://wiki.fysik.dtu.dk/ase/')
    return ase


def get_tof_names():
    tofs = []
    for process, tof_count in settings.tof_count.iteritems():
        for tof in tof_count:
            if tof not in tofs:
                tofs.append(tof)
    return sorted(tofs)
