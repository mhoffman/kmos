#!/usr/bin/env python
"""
A front-end module to run a compiled kMC model. The actual model is
imported in kmc_model.so and all parameters are stored in kmc_settings.py.

The model can be used directly like so::

    from kmos.model import KMC_Model
    model = KMC_Model()

    model.parameters.T = 500
    model.do_steps(100000)
    model.view()

which, of course can also be part of a python script.

The model can also be run in a different process using the
multiprocessing module. This mode is designed for use with
a GUI so that the CPU intensive kMC integration can run at
full throttle without impeding the front-end. Interaction with
the model happens through Queues.
"""

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

__all__ = ['base', 'lattice', 'proclist', 'KMC_Model']

from copy import deepcopy
import multiprocessing
import random
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
    """API Front-end to initialize and run a kMC model using python bindings.
    Depending on the constructor cal the model can be run either via directory
    calls or in a separate processes access via multiprocessing.Queues.
    Only one model instance can exist simultaneously per process."""

    def __init__(self, image_queue=None,
                       parameter_queue=None,
                       signal_queue=None,
                       size=None, system_name='kmc_model',
                       banner=True,
                       print_rates=True,
                       autosend=True):
        super(KMC_Model, self).__init__()
        self.image_queue = image_queue
        self.parameter_queue = parameter_queue
        self.signal_queue = signal_queue
        self.autosend = autosend
        self.print_rates = print_rates
        self.parameters = Model_Parameters(self.print_rates)
        self.rate_constants = Model_Rate_Constants()
        self.size = int(settings.simulation_size) \
                        if size is None else int(size)

        self.base = base
        self.lattice = lattice
        self.proclist = proclist
        self.settings = settings
        self.system_name = system_name
        self.banner = banner

        self.reset()

    def reset(self):
        self.size = int(settings.simulation_size)
        proclist.init((self.size,) * int(lattice.model_dimension),
            self.system_name,
            lattice.default_layer,
            not self.banner)
        self.cell_size = lattice.unit_cell_size * lattice.system_size

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
            if hasattr(settings, 'substrate_layer'):
                self.lattice_representation = eval(
                    settings.lattice_representation)[
                        lattice.substrate_layer]
            else:
                self.lattice_representation = eval(
                    settings.lattice_representation)[
                        lattice.default_layer]
        else:
            self.lattice_representation = Atoms()
        set_rate_constants(settings.parameters, self.print_rates)

    def __repr__(self):
        """Print short summary of current parameters and rate
        constants. It is advisable to include this at the beginning
        of every generated data file for later reconstruction
        """
        return (repr(self.parameters) + repr(self.rate_constants))

    def put(self, site, species):
        """Puts a certain species at a certain site.
        (Not implemented)
        """
        species = species.lower()

        cell, name = np.array(site[:3]), site[3].lower()
        site_nr = eval('lattice.%s' % name)
        site = np.array(list(cell) + [site_nr])
        species = lattice.get_species(site)
        if species:
            pass

    def get_occupation_header(self):
        """Returns the names of the fields returned by
        self.get_atoms().occupation.
        Useful for the header line of an ASCII output.
        """
        return ' '.join(['%s_%s' % (species, site)
                           for species in sorted(settings.representations)
                           for site in settings.site_names])

    def get_tof_header(self):
        """Returns the names of the fields returned by
        self.get_atoms().tof_data.
        Useful for the header line of an ASCII output.
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
            for _ in xrange(50000):
                proclist.do_kmc_step()
            if self.autosend and not self.image_queue.full():
                atoms = self.get_atoms()
                # attach other quantities need to plot
                # to the atoms object and let it travel
                # piggy-back through the queue
                atoms.size = self.size
                self.image_queue.put(atoms)
            if not self.signal_queue.empty():
                signal = self.signal_queue.get()
                if signal.upper() == 'STOP':
                    self.deallocate()
                    break
                elif signal.upper() == 'PAUSE':
                    print('starting pause')
                elif signal.upper() == 'RESET_TIME':
                    base.set_kmc_time(0.0)
                elif signal.upper() == 'START':
                    pass
                elif signal.upper() == 'ATOMS':
                    self.image_queue.put(self.get_atoms())
                elif signal.upper() == 'DOUBLE':
                    self.double()
                elif signal.upper() == 'HALVE':
                    self.halve()
                elif signal.upper() == 'SWITCH_SURFACE_PROCESSES_OFF':
                    self.switch_surface_processes_off()
                elif signal.upper() == 'SWITCH_SURFACE_PROCESSES_ON':
                    self.switch_surface_processes_on()


            if not self.parameter_queue.empty():
                while not self.parameter_queue.empty():
                    parameters = self.parameter_queue.get()
                    settings.parameters.update(parameters)
                set_rate_constants(parameters, self.print_rates)

    def view(self):
        """Visualize the current configuration of the model using ASE ag."""
        ase = import_ase()
        ase.visualize.view(self.get_atoms())

    def get_atoms(self, geometry=True):
        """Return an ASE Atoms object with additional
        information such as coverage and Turn-over-frequencies
        attached."""

        if geometry:
            ase = import_ase()
            atoms = ase.atoms.Atoms()
            for i in xrange(lattice.system_size[0]):
                for j in xrange(lattice.system_size[1]):
                    for k in xrange(lattice.system_size[2]):
                        for n in xrange(1, 1 + lattice.spuck):
                            species = lattice.get_species([i, j, k, n])
                            if self.species_representation[species]:
                                # create the atom
                                atom = deepcopy(
                                    self.species_representation[species])

                                # move to the correct location
                                atom.translate(
                                    np.dot(
                                        np.array([i, j, k]) +
                                        lattice.site_positions[n - 1],
                                            lattice.unit_cell_size))
                                # add to existing slab
                                atoms += atom
                        lattice_repr = deepcopy(self.lattice_representation)
                        lattice_repr.translate(np.dot(np.array([i, j, k]),
                                                      lattice.unit_cell_size))
                        atoms += lattice_repr
            atoms.set_cell(self.cell_size)
        else:

            class Expando():
                pass
            atoms = Expando()
        atoms.calc = None
        atoms.kmc_time = base.get_kmc_time()
        atoms.kmc_step = base.get_kmc_step()

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

    def double(self):
        """
        Double the size of the model in each direction and initialize
        larger model with current configuration in each copy.
        """

        config = self._get_configuration()
        old_system_size = deepcopy(self.lattice.system_size)

        # initialize new version of model w/ twice the size in each direction
        self.deallocate()
        self.settings.simulation_size *= 2
        self.reset()

        # initialize new model w/ copies of current state in each of
        # the new copies
        for x in range(self.lattice.system_size[0]):
            for y in range(self.lattice.system_size[1]):
                for z in range(self.lattice.system_size[2]):
                    xi, yi, zi = np.array([x, y, z]) % \
                                 old_system_size
                    for n in range(self.lattice.spuck):
                        self.lattice.replace_species(
                            [x, y, z, n + 1],
                            self.proclist.default_species,
                            config[xi, yi, zi, n],)
        self._adjust_database()

    def switch_surface_processes_off(self):
        """Set rate constant to zero if process
        has 'diff' or 'react' in the name.

        """
        for i, process_name in enumerate(
                               sorted(
                               self.settings.rate_constants)):
            if 'diff' in process_name or 'react' in process_name:
                self.base.set_rate_const(i + 1, .0)

    def  switch_surface_processes_on(self):
        set_rate_constants(settings.parameters, self.print_rates)

    def halve(self):
        """
        Halve the size of the model and initialize each site in the new model
        with a species randomly drawn from the sites that are reduced onto
        one. It is necessary that the simulation size is even
        """
        if self.settings.simulation_size % 2:
            print("Can only halve system with even size!")
            return

        config = self._get_configuration()

        self.deallocate()
        self.settings.simulation_size /= 2
        self.reset()

        X, Y, Z = self.lattice.system_size
        N = self.lattice.spuck
        for x in range(X):
            for y in range(Y):
                for z in range(Z):
                    for n in range(N):
                        # collect species
                        # from the 8 sites that are
                        # reduced onto one
                        choices = [config[(x + i * X) % X,
                                         (y + j * Y) % Y,
                                         (z + k * Z) % Z,
                                         n]
                            for i in range(2)
                            for j in range(2)
                            for k in range(2)]

                        # use random.choice
                        # to randomly select one
                        self.lattice.replace_species(
                            [x, y, z, n + 1],
                            self.proclist.default_species,
                            random.choice(choices))
        self._adjust_database()

    def _get_configuration(self):
        """ Return current configuration of model."""
        config = np.zeros(list(self.lattice.system_size) + \
            [int(self.lattice.spuck)])
        for x in range(self.lattice.system_size[0]):
            for y in range(self.lattice.system_size[1]):
                for z in range(self.lattice.system_size[2]):
                    for n in range(self.lattice.spuck):
                        config[x, y, z, n] = \
                            self.lattice.get_species(
                                [x, y, z, n + 1])
        return config

    def _set_configuration(self, config):
        """Set the current lattice configuration.

           Expects a 4-dimensional array, with dimensions [X, Y, Z, N]
           where X, Y, Z are the lattice size and N the number of
           sites in each unit cell."""
        X, Y, Z = self.lattice.system_size
        N = self.lattice.spuck
        if not all(config.shape == np.array([X, Y, Z, N])):
            print('Config shape %s does not match' % config.shape)
            print('with model shape %s.' % [X, Y, Z, N])
            return
        for x in range(X):
            for y in range(Y):
                for z in range(Z):
                    for n in range(N):
                        species = self.lattice.get_species([x, y, z, n + 1])
                        self.lattice.replace_species([x, y, z, n + 1],
                                                     species,
                                                     config[x, y, z, n])
        self._adjust_database()

    def _adjust_database(self):
        """Set the database of processes currently
        possible according to the current configuration."""
        for x in range(self.lattice.system_size[0]):
            for y in range(self.lattice.system_size[1]):
                for z in range(self.lattice.system_size[2]):
                    for n in range(self.lattice.spuck):
                        site_name = self.settings.site_names[n]
                        eval('self.proclist.touchup_%s([%i, %i, %i, %i])'
                            % (site_name, x, y, z, n + 1))

    def xml(self):
        """Returns the XML representation that this model was created from.
        """
        return settings.xml

    def nr2site(self, n):
        """Accepts a site index and return the site in human readable
        coordinates"""
        site = list(lattice.calculate_nr2lattice(n))
        site[-1] = settings.site_names[site[-1] - 1]
        return site

    def post_mortem(self, steps=None, propagate=False, err_code=None):
        """Accepts an integer and generates a post-mortem report
        by running that many steps and returning which process
        would be executed next without executing it.
        """
        if err_code is not None:
            old, new, found, err_site, steps = err_code
            err_site = self.nr2site(err_site)
            if old >= 0:
                old = sorted(settings.representations.keys())[old]
            else:
                old = 'NULL'

            if new >= 0:
                new = sorted(settings.representations.keys())[new]
            else:
                new = 'NULL'

            if found >= 0:
                found = sorted(settings.representations.keys())[found]
            else:
                found = 'NULL'

            self.do_steps(steps)
            nprocess, nsite = proclist.get_kmc_step()
            process = list(
                sorted(settings.rate_constants.keys()))[nprocess - 1]
            site = self.nr2site(nsite)
            print('=====================================')
            print('Post-Mortem Error Report')
            print('=====================================')
            print('  kmos ran %s steps and the next process is "%s"' %
                    (steps, process))
            print('  on site %s,  however this causes oops' % site)
            print('  on site %s because it trys to' % err_site)
            print('  replace "%s" by "%s" but it will find "%s".' %
                  (old, new, found))
            print('  Go fish!')

        else:
            if steps is not None:
                self.do_steps(steps)
            else:
                steps = base.get_kmc_step()
            nprocess, nsite = proclist.get_kmc_step()
            process = list(
                sorted(settings.rate_constants.keys()))[nprocess - 1]
            site = self.nr2site(nsite)

            res = "kmos ran %s steps and next it will execute\n" % steps
            res += "process '%s' on site %s." % (process, site)
            print(res)

            if propagate:
                proclist.run_proc_nr(nprocess, nsite)

    def procstat_pprint(self):
        """Print an overview view process names along with
        the number of times it has been executed."""
        for i, name in enumerate(sorted(self.settings.rate_constants.keys())):
            print('%s : %.4e' % (name, self.base.get_procstat(i + 1)))

    def procstat_normalized(self):
        """Print an overview view process names along with
        the number of times it has been executed divided by
        the current rate constant times the kmc time.

        Can help to find those processes which are kinetically
        hindered."""
        kmc_time = self.base.get_kmc_time()

        for i, name in enumerate(sorted(self.settings.rate_constants.keys())):
            if kmc_time:
                print('%s : %.4e' % (name, self.base.get_procstat(i + 1) /
                                           self.lattice.system_size.prod() /
                                           self.base.get_kmc_time() /
                                           self.base.get_rate(i + 1)))
            else:
                print('%s : %.4e' % (name, 0.))

    def rate_ratios(self):
        ratios = []
        for i, iname in enumerate(
                        sorted(self.settings.rate_constants.keys())):
            for j, jname in enumerate(
                            sorted(self.settings.rate_constants.keys())):
                if i != j:  # i == 1 -> 1., don't need that
                    irate = self.base.get_rate(i + 1)
                    jrate = self.base.get_rate(j + 1)
                    ratios.append(('%s/%s' % (iname, jname), irate / jrate))

        # sort ratios in descending order
        ratios.sort(key=lambda x: - x[1])
        res = ''
        for label, ratio in ratios:
            res += ('%s: %s\n' % (label, ratio))
        return res


class Model_Parameters(object):
    """Holds all user defined parameters of a model in
    concise form. All user defined parameters can be
    accessed and set as attributes, like so ::

        model.parameters.<parameter> = X.Y
    """

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
        res = '# kMC model parameters (%i)\n' % len(settings.parameters)
        res += '# --------------------\n'
        for attr in sorted(settings.parameters):
            res += ('# %s = %s\n' % (attr, settings.parameters[attr]['value']))
        res += '# --------------------\n'
        return res


class Model_Rate_Constants(object):

    def __repr__(self):
        """Compact representation of all current rate_constants."""
        res = '# kMC rate constants (%i)\n' % len(settings.rate_constants)
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
    For the evaluation it draws on predefined natural constants, user defined
    parameters and mathematical functions.
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
                n = int(4 * log(rate_const))
                print('%30s: %.3e s^{-1}: %s' % (proc, rate_const, '#' * n))
        except Exception, e:
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
