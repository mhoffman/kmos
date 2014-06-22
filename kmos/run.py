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

__all__ = ['base', 'lattice', 'proclist', 'KMC_Model']

from ase.atoms import Atoms
from copy import deepcopy
from fnmatch import fnmatch
from kmos import evaluate_rate_expression
from kmos.utils import OrderedDict
from math import log
from multiprocessing import Process
import numpy as np
import os
import random
import sys
try:
    from kmc_model import base, lattice, proclist
except Exception, e:
    base = lattice = proclist = None
    print("""Error: %s
    Could not find the kmc module. The kmc implements the actual
    kmc model. This can be created from a kmos xml file using
    kmos export <xml-file>
    Hint: are you in a directory containing a compiled kMC model?\n\n
    """ % e)

try:
    from kmc_model import proclist_constants
except:
    proclist_constants = None

try:
    import kmc_settings as settings
except Exception, e:
    settings = None
    print("""Error %s
    Could import settings file
    The kmc_settings.py contains all changeable model parameters
    and descriptions for the representation on screen.
    Hint: are you in a directory containing a compiled kMC model?
    """ % e)


INTERACTIVE = hasattr(sys, 'ps1') or hasattr(sys, 'ipcompleter')
INTERACTIVE = True  # Turn it off for now because it doesn work reliably


class ProclistProxy(object):

    def __dir__(selftr):
        return list(set(dir(proclist) + dir(proclist_constants)))

    def __getattr__(self, attr):
        if attr in dir(proclist):
            return eval('proclist.%s' % attr)
        elif attr in dir(proclist_constants):
            return eval('proclist_constants.%s' % attr)
        else:
            raise AttributeError('%s not found' % attr)


class KMC_Model(Process):
    """API Front-end to initialize and run a kMC model using python bindings.
    Depending on the constructor call the model can be run either via directory
    calls or in a separate processes access via multiprocessing.Queues.
    Only one model instance can exist simultaneously per process."""

    def __init__(self, image_queue=None,
                       parameter_queue=None,
                       signal_queue=None,
                       size=None, system_name='kmc_model',
                       banner=True,
                       print_rates=False,
                       autosend=True,
                       steps_per_frame=50000,
                       random_seed=None,
                       cache_file=None):

        # initialize multiprocessing.Process hooks
        super(KMC_Model, self).__init__()

        # setup queues for viewer
        self.image_queue = image_queue
        self.parameter_queue = parameter_queue
        self.signal_queue = signal_queue
        self.autosend = autosend

        # initalize instance settings
        self.system_name = system_name
        self.banner = banner
        self.print_rates = print_rates
        self.parameters = Model_Parameters(self.print_rates)
        self.rate_constants = Model_Rate_Constants()

        if random_seed is not None:
            settings.random_seed = random_seed

        if size is None:
            size = settings.simulation_size
        if isinstance(size, int):
            self.size = np.array([size] * int(lattice.model_dimension))
        elif isinstance(size, (tuple, list)):
            if not len(size) == lattice.model_dimension:
                raise UserWarning(('You requested a size %s '
                                   '(i. e. %s dimensions),\n '
                                   'but the compiled model'
                                   'has %s dimensions!')
                                   % (list(size),
                                      len(size),
                                      lattice.model_dimension))
            self.size = np.array(size)

        self.steps_per_frame = steps_per_frame
        self.cache_file = cache_file

        # bind Fortran submodules
        self.base = base
        self.lattice = lattice
        self.proclist = ProclistProxy()
        self.settings = settings

        if hasattr(self.base, 'null_species'):
            self.null_species = self.base.null_species
        elif hasattr(self.base, 'get_null_species'):
            self.null_species = self.base.get_null_species()
        else:
            self.null_species = -1


        self.proclist.seed = np.array(getattr(self.settings, 'random_seed', 1))
        self.reset()

        if hasattr(settings, 'setup_model'):
            import new
            self.setup_model = new.instancemethod(settings.setup_model,
                                                  self,
                                                  KMC_Model)
            self.setup_model()

    def __enter__(self, *args, **kwargs):
        """__enter/exit__ function for with-statement protocol."""
        return self

    def __exit__(self, exc_type, exc_value, exc_tb):
        """__enter/exit__ function for with-statement protocol."""
        self.deallocate()

    def reset(self):
        self.size = np.array(self.size)
        try:
            proclist.init(self.size,
                self.system_name,
                lattice.default_layer,
                self.settings.random_seed,
                not self.banner)
        except:
            # fallback if API
            # does not support random seed.
            proclist.init(self.size,
                self.system_name,
                lattice.default_layer,
                not self.banner)
        self.cell_size = np.dot(np.diag(lattice.system_size), lattice.unit_cell_size)

        # prepare structures for TOF evaluation
        self.tofs = tofs = get_tof_names()
        self.tof_matrix = np.zeros((len(tofs), proclist.nr_of_proc))
        for process, tof_count in sorted(settings.tof_count.iteritems()):
            process_nr = getattr(self.proclist, process.lower())
            for tof, tof_factor in tof_count.iteritems():
                self.tof_matrix[tofs.index(tof), process_nr - 1] += tof_factor

        # prepare procstat
        self.procstat = np.zeros((proclist.nr_of_proc), dtype=np.int64)
         # prepare integ_rates (S.Matera 09/25/2012)
        self.integ_rates = np.zeros((proclist.nr_of_proc, ))
        self.time = 0.
        self.steps = 0

        self.species_representation = {}
        for species in sorted(settings.representations):
            if settings.representations[species].strip():
                try:
                    self.species_representation[len(self.species_representation)] \
                    = eval(settings.representations[species])
                except Exception, e:
                    print('Trouble with representation %s'
                           % settings.representations[species])
                    print(e)
                    raise
            else:
                self.species_representation[len(self.species_representation)] = Atoms()
        if hasattr(settings, 'species_tags'):
            self.species_tags = settings.species_tags
        else:
            self.species_tags = None

        if len(settings.lattice_representation):
            if hasattr(settings, 'substrate_layer'):
                self.lattice_representation = eval(
                    settings.lattice_representation)[
                        lattice.substrate_layer]
            else:
                lattice_representation = eval(
                    settings.lattice_representation)
                if len(lattice_representation) > 1:
                    self.lattice_representation = \
                         lattice_representation[self.lattice.default_layer]
                else:
                    self.lattice_representation = lattice_representation[0]
        else:
            self.lattice_representation = Atoms()
        set_rate_constants(settings.parameters, self.print_rates)
        self.base.update_accum_rate()
        # S. matera 09/25/2012
        if hasattr(self.base, 'update_integ_rate'):
            self.base.update_integ_rate()

        # load cached configuration if available
        if self.cache_file is not None:
            if os.path.exists(self.cache_file):
                self.load_config(self.cache_file)

    def __repr__(self):
        """Print short summary of current parameters and rate
        constants. It is advisable to include this at the beginning
        of every generated data file for later reconstruction
        """
        return (repr(self.parameters) + repr(self.rate_constants))

    def inverse(self):
        return (repr(self.parameters) + self.rate_constants.inverse())

    def get_param_header(self):
        """Return the names of field return by
        self.get_atoms().params.
        Useful for the header line of an ASCII output.
        """
        return ' '.join(param_name
                       for param_name in sorted(self.settings.parameters)
            if self.settings.parameters[param_name].get('adjustable', False))

    def get_occupation_header(self):
        """Return the names of the fields returned by
        self.get_atoms().occupation.
        Useful for the header line of an ASCII output.
        """
        return ' '.join(['%s_%s' % (species, site)
                           for species in sorted(settings.representations)
                           for site in settings.site_names])

    def get_tof_header(self):
        """Return the names of the fields returned by
        self.get_atoms().tof_data.
        Useful for the header line of an ASCII output.
        """
        tofs = []
        for _, value in settings.tof_count.iteritems():
            for name in value:
                if name not in tofs:
                    tofs.append(name)
        tofs.sort()
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

        if self.cache_file is not None:
            # create directory if necessary
            dirname = os.path.dirname(self.cache_file)
            if dirname and not os.path.exists(dirname):
                os.makedirs(dirname)
            self.dump_config(self.cache_file)

        if bool(base.is_allocated()):
            lattice.deallocate_system()
        else:
            print("Model is not allocated.")

    def do_steps(self, n=10000):
        """Propagate the model `n` steps.

        :param n: Number of steps to run (Default: 10000)
        :type n: int

        """
        proclist.do_kmc_steps(n)

    def run(self):
        """Runs the model indefinitely. To control the
        simulations, model must have been initialized
        with proper Queues."""
        if not base.is_allocated():
            self.reset()
        while True:
            for _ in xrange(self.steps_per_frame):
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
                    print('Doubling model size')
                    self.double()
                elif signal.upper() == 'HALVE':
                    print('Halving model size')
                    self.halve()
                elif signal.upper() == 'SWITCH_SURFACE_PROCESSES_OFF':
                    self.switch_surface_processes_off()
                elif signal.upper() == 'SWITCH_SURFACE_PROCESSES_ON':
                    self.switch_surface_processes_on()
                elif signal.upper() == 'TERMINATE':
                    self.deallocate()
                    self.terminate()
                elif signal.upper() == 'JOIN':
                    self.join()
                elif signal.upper() == 'WRITEOUT':
                    atoms = self.get_atoms()
                    step = self.base.get_kmc_step()
                    from ase.io import write
                    filename = '%s_%s.traj' % (self.settings.model_name, step)
                    print('Wrote snapshot to %s' % filename)
                    write(filename, atoms)
                elif signal.upper() == 'ACCUM_RATE_SUMMATION':
                    self.print_accum_rate_summation()
                elif signal.upper() == 'COVERAGE':
                    self.print_coverages()

            if not self.parameter_queue.empty():
                while not self.parameter_queue.empty():
                    parameters = self.parameter_queue.get()
                    settings.parameters.update(parameters)
                set_rate_constants(parameters, self.print_rates)

    def export_movie(self,
                    frames=30,
                    skip=1,
                    prefix='movie',
                    rotation='15z,-70x',
                    suffix='png',
                    **kwargs):
        """Export series of snapshots of model instance to an image
        file in the current directory which allows for easy post-processing
        of images, e.g. using `ffmpeg` ::

            ffmpeg -i movie_%06d.png -f image2 -r 24 movie.avi

        Allows suffixes are png, pov, and eps. Additional keyword arguments
        (kwargs) are passed directly the ase.io.write of the ASE library.

        When exporting to *.pov, one has to manually povray each *.pov file in
        the directory which is as simple as typing ::

            for pov_file in *.pov
            do
               povray ${pov_file}
            done

        using bash.

        :param frames: Number of frames to records (Default: 30).
        :type frames: int
        :param skip: Number of kMC steps between frames (Default: 1).
        :type skip: int
        :param prefix: Prefix for filename (Default: movie).
        :type prefix: str
        :param rotation: Angle from which movie is recorded
                         (only useful if suffix is png).
                         String to be interpreted by ASE (Default: '15x,-70x')
        :type rotation: str
        :param suffix: File suffix (type) of exported file (Default: png).
        :type suffix: str

        """

        from ase.io import write
        for i in xrange(frames):
            atoms = self.get_atoms()
            write('%s_%06i.%s' % (prefix, i, suffix),
                  atoms,
                  show_unit_cell=True,
                  rotation=rotation,
                  **kwargs)
            self.do_steps(skip)

    def show(self, *args, **kwargs):
        """Visualize the current configuration of the model using ASE ag."""
        tag = kwargs.pop('tag', None)

        ase = import_ase()
        ase.visualize.view(self.get_atoms(tag=tag), *args, **kwargs)

    def view(self):
        """Start current model in live view mode."""
        from kmos import view
        view.main(self)

    def get_atoms(self, geometry=True, tag=None):
        """Return an ASE Atoms object with additional
        information such as coverage and Turn-over-frequencies
        attached.

        The additional attributes are:
          - `info` (extra tags assigned to species)
          - `kmc_step`
          - `kmc_time`
          - `occupation`
          - `procstat`
          - `integ_rates`
          - `tof_data`

        `tof_data` contains previously defined TOFs in reaction per seconds per
                   cell sampled since the last call to `get_atoms()`
        `info` can be used to better visualize similar looking molecule during
               post-processing
        `procstat` holds the number of times each process was executed since
                   last `get_atoms()` call.


        :param geometry: Return ASE object of current configuration
                         (Default: True).
        :type geometry: bool

        """

        if geometry:
            kmos_tags = {}
            ase = import_ase()
            atoms = ase.atoms.Atoms()
            for i in xrange(lattice.system_size[0]):
                for j in xrange(lattice.system_size[1]):
                    for k in xrange(lattice.system_size[2]):
                        for n in xrange(1, 1 + lattice.spuck):
                            species = lattice.get_species([i, j, k, n])
                            if species == self.null_species:
                                continue
                            if self.species_representation.get(species, ''):
                                # create the ad_atoms
                                ad_atoms = deepcopy(
                                    self.species_representation[species])

                                if tag == 'species':
                                    ad_atoms.set_initial_magnetic_moments([species] * len(ad_atoms))
                                elif tag == 'site':
                                    ad_atoms.set_initial_magnetic_moments([n] * len(ad_atoms))
                                elif tag == 'x':
                                    ad_atoms.set_initial_magnetic_moments([i] * len(ad_atoms))
                                elif tag == 'y':
                                    ad_atoms.set_initial_magnetic_moments([j] * len(ad_atoms))
                                elif tag == 'z':
                                    ad_atoms.set_initial_magnetic_moments([k] * len(ad_atoms))

                                # move to the correct location
                                ad_atoms.translate(
                                    np.dot(
                                        np.array([i, j, k]) +
                                        lattice.site_positions[n - 1],
                                            lattice.unit_cell_size))
                                # add to existing slab
                                atoms += ad_atoms
                                if self.species_tags:
                                    for atom in range(len(atoms)
                                                      - len(ad_atoms),
                                                      len(atoms)):
                                        kmos_tags[atom] = \
                                        self.species_tags.values()[species]

                        if self.lattice_representation:
                            lattice_repr = deepcopy(self.lattice_representation)
                            lattice_repr.translate(np.dot(np.array([i, j, k]),
                                                          lattice.unit_cell_size))
                            atoms += lattice_repr
            atoms.set_cell(self.cell_size)

            # workaround for older ASE < 3.6
            if not hasattr(atoms, 'info'):
                atoms.info = {}

            atoms.info['kmos_tags'] = kmos_tags
        else:

            class Expando():
                pass
            atoms = Expando()
        atoms.calc = None
        atoms.kmc_time = base.get_kmc_time()
        atoms.kmc_step = base.get_kmc_step()
        atoms.params = [float(self.settings.parameters.get(param_name)['value'])
                   for param_name in sorted(self.settings.parameters)
        if self.settings.parameters[param_name].get('adjustable', False)]

        # calculate TOF since last call
        atoms.procstat = np.zeros((proclist.nr_of_proc,))
        atoms.occupation = proclist.get_occupation()
        for i in range(proclist.nr_of_proc):
            atoms.procstat[i] = base.get_procstat(i + 1)
        # S. Matera 09/25/2012
        if hasattr(self.base, 'get_integ_rate'):
            atoms.integ_rates = np.zeros((proclist.nr_of_proc,))
            for i in range(proclist.nr_of_proc):
                    atoms.integ_rates[i] = base.get_integ_rate(i + 1)
        # S. Matera 09/25/2012
        delta_t = (atoms.kmc_time - self.time)
        delta_steps = atoms.kmc_step - self.steps
        atoms.delta_t = delta_t
        size = self.size.prod()
        if delta_steps == 0:
            # if we haven't done any steps, return the last TOF again
            atoms.tof_data = self.tof_data if hasattr(self, 'tof_data') else np.zeros_like(self.tof_matrix[:, 0])
            atoms.tof_integ = self.tof_integ  if hasattr(self, 'tof_integ') else np.zeros_like(self.tof_matrix[:, 0])
        elif delta_t == 0. and atoms.kmc_time > 0:
            print(
                "Warning: numerical precision too low, to resolve time-steps")
            print('         Will reset kMC time to 0s.')
            base.set_kmc_time(0.0)
            atoms.tof_data = np.zeros_like(self.tof_matrix[:, 0])
            atoms.tof_integ = np.zeros_like(self.tof_matrix[:, 0])

        else:
            atoms.tof_data = np.dot(self.tof_matrix,
                            (atoms.procstat - self.procstat) / delta_t / size)
            # S. Matera 09/25/2012
            if hasattr(self.base, 'get_integ_rate'):
                atoms.tof_integ = np.dot(self.tof_matrix,
                                (atoms.integ_rates - self.integ_rates)
                                / delta_t / size)
            # S. Matera 09/25/2012

        atoms.delta_t = delta_t

        # update trackers for next call
        self.procstat[:] = atoms.procstat
        # S. Matera 09/25/2012
        if hasattr(self.base, 'get_integ_rate'):
            self.integ_rates[:] = atoms.integ_rates
        # S. Matera 09/25/2012
        self.time = atoms.kmc_time
        self.step = atoms.kmc_step
        self.tof_data = atoms.tof_data
        self.tof_integ = atoms.tof_integ

        return atoms

    def get_std_header(self):
        """Return commented line of field names corresponding to
        values returned in get_std_outdata

        """

        std_header = ('#%s %s %s kmc_time kmc_steps\n'
                  % (self.get_param_header(),
                     self.get_tof_header(),
                     self.get_occupation_header()))
        return std_header

    def get_std_sampled_data(self, samples, sample_size, tof_method='integ'):
        """Sample an average model and return TOFs and coverages
        in a standardized format :

        [parameters] [TOFs] [occupations] kmc_time kmc_step

        Parameter tof_method allows to switch between two different methods for
        evaluating turn-over-frequencies. The default method *procstat* evaluates
        the procstat counter, i.e. simply the number of executed events in the
        simulated time interval. *integ* will evaluate the number of times the
        reaction `could` be evaluated in the simulated time interval
        based on the local configurations and the rate constant.

        Credit for this latter method has to be given to Sebastian Matera for
        the idea and implementation.

        In each case check carefully that the observable is sampled good enough!

        :param samples: Number of batches to average over.
        :type sample: int
        :param sample_size: Number of kMC steps per batch.
        :type sample_size: int
        :param tof_method: Method of how to sample TOFs.
                           Possible values are procrates or integ.
                           While procrates only counts the processes actually executed,
                           integ evaluates the configuration to estimate the actual
                           rates. The latter can be several orders more efficient
                           for very slow processes.
                           Differences resulting from the two methods can be used
                           as on estimate for the statistical error in samples.
        :type tof_method: str

        """

        # initialize lists for averages
        occs = []
        tofs = []
        delta_ts = []
        t0 = self.base.get_kmc_time()
        step0 = self.base.get_kmc_step()

        # sample over trajectory
        for sample in xrange(samples):
            self.do_steps(sample_size)
            atoms = self.get_atoms(geometry=False)

            delta_ts.append(atoms.delta_t)

            occs.append(list(atoms.occupation.flatten()))
            if tof_method == 'procrates':
                tofs.append(atoms.tof_data.flatten())
            elif tof_method == 'integ':
                tofs.append(atoms.tof_integ.flatten())
            else:
                raise NotImplementedError('Working on it ..')

        # calculate time averages
        occs_mean = np.average(occs, axis=0, weights=delta_ts)
        tof_mean = np.average(tofs, axis=0, weights=delta_ts)
        total_time = self.base.get_kmc_time() - t0
        total_steps = self.base.get_kmc_step() - step0

        #return tofs, delta_ts

        # write out averages
        outdata = tuple(atoms.params
                        + list(tof_mean.flatten())
                        + list(occs_mean.flatten())
                        + [total_time,
                           total_steps])
        return ((' '.join(['%.5e'] * len(outdata)) + '\n') % outdata)

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
                    xi, yi, zi = np.array([x, y, z]) % old_system_size
                    for n in range(self.lattice.spuck):
                        self.lattice.replace_species(
                            [x, y, z, n + 1],
                            self.lattice.get_species([x, y, z, n + 1]),
                            config[xi, yi, zi, n])
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

    def switch_surface_processes_on(self):
        set_rate_constants(settings.parameters, self.print_rates)

    def print_adjustable_parameters(self, match=None, to_stdout=True):
        """Print those methods that are adjustable via the GUI.

        :param pattern: fname pattern to limit the parameters.
        :type pattern: str
        """
        res = ''
        w = 80
        res += (w * '-') + '\n'
        for i, attr in enumerate(sorted(self.settings.parameters)):
            if (match is None or fnmatch(attr, match))\
                and settings.parameters[attr]['adjustable']:
                res += '|{0:^78s}|\n'.format((' %40s = %s'
                      % (attr, settings.parameters[attr]['value'])))
        res += (w * '-') + '\n'
        if to_stdout:
            print(res)
        else:
            return res

    def print_coverages(self, to_stdout=True):
        """Show coverages (per unit cell) for each species
        and site type for current configurations.

        """

        res = ''
        # get atoms
        atoms = self.get_atoms(geometry=False)

        # get occupation
        occupation = atoms.occupation

        # get species names
        species_names = sorted(self.settings.representations.keys())

        # get site_names
        site_names = sorted(self.settings.site_names)

        header_line = ('|' +
                      ('%18s|' % 'site \ species') +
                      '|'.join([('%11s' % sn)
                                for sn in species_names] + ['']))
        res += '%s\n' % (len(header_line) * '-')
        res += '%s\n' % header_line
        res += '%s\n' % (len(header_line) * '-')
        for i in range(self.lattice.spuck):
            site_name = self.settings.site_names[i]
            res += '%s\n' % ('|'
                 + '{0:<18s}|'.format(site_name)
                 + '|'.join([('{0:^11.5f}'.format(x) if x else 11 * ' ')
                             for x in list(occupation[:, i])]
                 + ['']))
        res += '%s\n' % (len(header_line) * '-')
        res += '%s\n' % ('Units: "molecules (or atoms) per unit cell"')
        if to_stdout:
            print(res)
        else:
            return res

    def print_procstat(self, to_stdout=True):
        entries = []
        longest_name = 0
        for i, process_name in enumerate(
                               sorted(
                               self.settings.rate_constants)):
            procstat = self.base.get_procstat(i + 1)
            namelength = len(process_name)
            if namelength > longest_name:
                longest_name = namelength
            entries.append((procstat, process_name))

        entries = sorted(entries, key=lambda x: - x[0])
        nsteps = self.base.get_kmc_step()

        width = longest_name + 30

        res = ''
        printed_steps = 0
        res += ('+' + width * '-' + '+' + '\n')
        for entry in entries:
            procstat, name = entry
            printed_steps += procstat
            if procstat:
                res += ('|{0:<%ss}|\n' % width).format('%9.2f %% %12s     %s' % (100 * float(printed_steps) / nsteps, procstat, name))

        res += ('+' + width * '-' + '+' + '\n')
        res += ('   Total steps %s' % nsteps)

        if to_stdout:
            print(res)
        else:
            return res

    def print_accum_rate_summation(self, order='-rate', to_stdout=True):
        """Shows rate individual processes contribute to the total rate

        The optional argument order can be one of: name, rate, rate_constant,
        nrofsites. You precede each keyword with a '-', to show in decreasing
        order.
        Default: '-rate'.

        """
        accum_rate = 0.
        entries = []
        # collect
        for i, process_name in enumerate(
                               sorted(
                               self.settings.rate_constants)):
            nrofsites = self.base.get_nrofsites(i + 1)
            if nrofsites:
                rate = self.base.get_rate(i + 1)
                prod = nrofsites * rate
                accum_rate += prod
                entries.append((nrofsites, rate, prod, process_name))

        # reorder
        if order == 'name':
            entries = sorted(entries, key=lambda x: x[3])
        elif order == 'rate':
            entries = sorted(entries, key=lambda x: x[2])
        elif order == 'rate_constant':
            entries = sorted(entries, key=lambda x: x[1])
        elif order == 'nrofsites':
            entries = sorted(entries, key=lambda x: x[0])
        elif order == '-name':
            entries = reversed(sorted(entries, key=lambda x: x[3]))
        elif order == '-rate':
            entries = reversed(sorted(entries, key=lambda x: x[2]))
        elif order == '-rate_constant':
            entries = reversed(sorted(entries, key=lambda x: x[1]))
        elif order == '-nrofsites':
            entries = reversed(sorted(entries, key=lambda x: x[0]))

        # print
        res = ''
        total_contribution = 0
        res += ('+' + 118 * '-' + '+' + '\n')
        res += '|{0:<118s}|\n'.format('(cumulative)    nrofsites * rate_constant'
                                      '    = rate            [name]')
        res += ('+' + 118 * '-' + '+' + '\n')
        for entry in entries:
            total_contribution += float(entry[2])
            percent = '(%8.4f %%)' % (total_contribution * 100 / accum_rate)
            entry = '% 12i * % 8.4e s^-1 = %8.4e s^-1 [%s]' % entry
            res += '|{0:<118s}|\n'.format('%s %s' % (percent, entry))

        res += ('+' + 118 * '-' + '+' + '\n')
        res += '|{0:<118s}|\n'.format(('  = total rate = %.8e s^-1'
                                       % accum_rate))
        res += ('+' + 118 * '-' + '+' + '\n')

        if to_stdout:
            print(res)
        else:
            return res

    def _put(self, site, new_species, reduce=False):
        """
        Works exactly like put, but without updating the database of
        available processes. This is faster for when one does a lot updates
        at once, however one must call _adjust_database afterwards.

        Examples ::

            model._put([0,0,0,model.lattice.lattice_bridge], model.proclist.co])
            # puts a CO molecule at the `bridge` site of the lower left unit cell

            model._put([1,0,0,model.lattice.lattice_bridge], model.proclist.co ])
            # puts a CO molecule at the `bridge` site one to the right

            # ... many more

            model._adjust_database() # Important !

        :param site: Site where to put the new species, i.e. [x, y, z, bridge]
        :type site: list or np.array
        :param new_species: Name of new species.
        :type new_species: str
        :param reduce: Of periodic boundary conditions if site falls out
                       site lattice (Default: False)
        :type reduce: bool

        """
        x, y, z, n = site
        if reduce:
            x, y, z = (x, y, z) % self.lattice.system_size
            site = np.array([x, y, z, n])

        # Error checking
        if not x in range(self.lattice.system_size[0]):
            raise UserWarning('x-coordinate %s seems to fall outside lattice'
                              % x)
        if not y in range(self.lattice.system_size[1]):
            raise UserWarning('y-coordinate %s seems to fall outside lattice'
                              % y)
        if not z in range(self.lattice.system_size[2]):
            raise UserWarning('z-coordinate %s seems to fall outside lattice'
                              % z)
        if not n in range(1, self.lattice.spuck + 1):
            raise UserWarning('n-coordinate %s seems to fall outside lattice'
                              % n)

        old_species = self.lattice.get_species(site)
        self.lattice.replace_species(site, old_species, new_species)

    def put(self, site, new_species, reduce=False):
        """
        Puts new_species at site. The site is given by 4-entry sequence
        like [x, y, z, n], where the first 3 entries define the unit cell
        from 0 to the number of unit cells in the respective direction.
        And `n` specifies the site within the unit cell.

        The database of available processes will be updated automatically.

        Examples ::

            model.put([0,0,0,model.lattice.site], model.proclist.co ])
            # puts a CO molecule at the `bridge` site
            # of the lower left unit cell

        :param site: Site where to put the new species, i.e. [x, y, z, bridge]
        :type site: list or np.array
        :param new_species: Name of new species.
        :type new_species: str
        :param reduce: Of periodic boundary conditions if site falls out site
                       lattice (Default: False)
        :type reduce: bool

        """

        self._put(site, new_species, reduce=reduce)
        self._adjust_database()

    def halve(self):
        """
        Halve the size of the model and initialize each site in the new model
        with a species randomly drawn from the sites that are reduced onto
        one. It is necessary that the simulation size is even.
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
                            self.lattice.get_species([x, y, z, n + 1]),
                            random.choice(choices))
        self._adjust_database()

    def run_proc_nr(self, proc, site):
        if self.base.get_avail_site(proc, site, 2):
            self.proclist.run_proc_nr(proc, site)
            return True
        else:
            print("Process not enabled")
            return False

    def get_next_kmc_step(self):
        proc, site = proclist.get_next_kmc_step()
        return ProcInt(proc), SiteInt(site)

    def get_avail(self, arg):
        """Return available (enabled) processes or sites
           :param arg: type or process to query
           :type arg: int or [int]

        """

        avail = []
        try:
            arg = list(iter(arg))
            # if is iterable, interpret as site
            site = self.lattice.calculate_lattice2nr([arg[0], arg[1], arg[2], 1])
            for process in range(1, self.proclist.nr_of_proc + 1):
                if self.base.get_avail_site(process, site, 2):
                    avail.append(ProcInt(process, self.settings))

        except Exception, e:
            # if is not iterable, interpret as process
            for x in range(self.lattice.system_size[0]):
                for y in range(self.lattice.system_size[1]):
                    for z in range(self.lattice.system_size[2]):
                        nr = self.lattice.calculate_lattice2nr([x, y, z, 1])
                        if self.base.get_avail_site(arg, nr, 2):
                            avail.append(SiteInt(nr))
        return avail

    def _get_configuration(self):
        """ Return current configuration of model.

           :rtype: np.array
        """
        config = np.zeros(list(self.lattice.system_size) + \
            [int(self.lattice.spuck)], dtype=np.int8)
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
           sites in each unit cell.

           :param config: Configuration to set for model. Shape of array
                          has to match with model size.
           :type config: np.array

        """
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
        possible according to the current configuration.

        """
        for x in range(self.lattice.system_size[0]):
            for y in range(self.lattice.system_size[1]):
                for z in range(self.lattice.system_size[2]):
                    if self.get_backend() == 'lat_int':
                        eval('self.proclist.touchup_cell([%i, %i, %i, 0])'
                            % (x, y, z))
                    else:
                        for n in range(self.lattice.spuck):
                            site_name = self.settings.site_names[n].lower()
                            eval('self.proclist.touchup_%s([%i, %i, %i, %i])'
                                % (site_name, x, y, z, n + 1))
        # DEBUGGING, adjust database
        self.base.update_accum_rate()

    def get_backend(self):
        """Return name of backend that model was compiled with.

        :rtype: str

        """
        if hasattr(self.proclist, 'backend'):
            try:
                return ''.join(self.proclist.backend)
            except:
                return '???'
        else:
            return 'local_smart'

    def xml(self):
        """Returns the XML representation that this model was created from.

        :rtype: str
        """
        return settings.xml

    def nr2site(self, n):
        """Accepts a site index and return the site in human readable
        coordinates.

        :param n: Index of site.
        :type n: int
        :rtype: str
        """
        site = list(lattice.calculate_nr2lattice(n))
        site[-1] = settings.site_names[site[-1] - 1]
        return site

    def post_mortem(self, steps=None, propagate=False, err_code=None):
        """Accepts an integer and generates a post-mortem report
        by running that many steps and returning which process
        would be executed next without executing it.

        :param steps: Number of steps to run before exit occurs
                     (Default: None).
        :type steps: int
        :param propagate: Run this one more step, where error occurs
                          (Default: False).
        :type propagate: bool
        :param err_code: Error code generated by backend if
                         project.meta.debug > 0 at compile time.
        :type err_code: str
        """
        if err_code is not None:
            old, new, found, err_site, steps = err_code
            err_site = self.nr2site(err_site)
            if old >= 0:
                old = sorted(settings.representations.keys())[old]
            else:
                old = 'NULL (%s)' % old

            if new >= 0:
                new = sorted(settings.representations.keys())[new]
            else:
                new = 'NULL (%s)' % new

            if found >= 0:
                found = sorted(settings.representations.keys())[found]
            else:
                found = 'NULL (%s)' % found

            self.do_steps(steps)
            nprocess, nsite = proclist.get_next_kmc_step()
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
            nprocess, nsite = proclist.get_next_kmc_step()
            process = list(
                sorted(settings.rate_constants.keys()))[nprocess - 1]
            site = self.nr2site(nsite)

            res = "kmos ran %s steps and next it will execute\n" % steps
            res += "process '%s' on site %s." % (process, site)
            print(res)

            if propagate:
                proclist.run_proc_nr(nprocess, nsite)

    def procstat_pprint(self, match=None):
        """Print an overview view process names along with
        the number of times it has been executed.

        :param match: fname pattern to filter matching parameter name.
        :type match: str

        """

        for i, name in enumerate(sorted(self.settings.rate_constants.keys())):
            if match is None:
                print('%s : %.4e' % (name, self.base.get_procstat(i + 1)))
            else:
                if fnmatch(name, match):
                    print('%s : %.4e' % (name, self.base.get_procstat(i + 1)))

    def procstat_normalized(self, match=None):
        """Print an overview view process names along with
        the number of times it has been executed divided by
        the current rate constant times the kmc time.

        Can help to find those processes which are kinetically
        hindered.

        :param match: fname pattern to filter matching parameter name.
        :type match: str

        """
        kmc_time = self.base.get_kmc_time()

        for i, name in enumerate(sorted(self.settings.rate_constants.keys())):
            if match is None or fnmatch(name, match):
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
        if INTERACTIVE:
            print(res)
        else:
            return res

    def dump_config(self, filename):
        """Use numpy mechanism to store current configuration in a file.

        :param filename: Name of file, to write configuration to.
        :type filename: str

        """
        np.save('%s.npy' % filename, self._get_configuration())

    def load_config(self, filename):
        """Use numpy mechanism to load configuration from a file. User
        must ensure that size of stored configuration is correct.

        :param filename: Name of file, to write configuration to.
        :type filename: str

        """
        x, y, z = self.lattice.system_size
        spuck = self.lattice.spuck
        config = np.load('%s.npy' % filename)

        self._set_configuration(config)
        self._adjust_database()


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
        if not attr in settings.parameters \
           and not attr in ['print_rates']:
            print("Warning: don't know parameter '%s'." % attr)
        if attr in settings.parameters:
            settings.parameters[attr]['value'] = value
            set_rate_constants(print_rates=self.print_rates)
        else:
            self.__dict__[attr] = value

    def __repr__(self):
        fixed_parameters = dict((name, param)
                                for name, param
                                in settings.parameters.items()
                                if not param['adjustable'])
        res = '# kMC model parameters (%i, fixed %i)\n' \
               % (len(settings.parameters), len(fixed_parameters))
        res += '# --------------------\n'
        for attr in sorted(settings.parameters):
            res += ('# %s = %s' % (attr, settings.parameters[attr]['value']))
            if settings.parameters[attr]['adjustable']:
                res += '  # *\n'
            else:
                res += '\n'
        res += '# --------------------\n'
        if not len(fixed_parameters) == len(settings.parameters):
            res += '# * adjustable parameters\n'
        return res

    def names(self, pattern=None):
        """Return names of parameters that match `pattern'

        :param pattern: fname pattern to filter matching parameter name.
        :type pattern: str

        """
        names = []
        for attr in sorted(settings.parameters):
            if pattern is None or fnmatch(attr, pattern):
                names.append(attr)
        return names

    def __call__(self, match=None, interactive=False):
        """Return parameters that match `pattern'

        :param match: fname pattern to filter matching parameter name.
        :type match: str

        """
        res = ''
        for attr in sorted(settings.parameters):
            if match is None or fnmatch(attr, match):
                res += ('# %s = %s\n'
                      % (attr, settings.parameters[attr]['value']))
        if INTERACTIVE:
            print(res)
        else:
            return res


class Model_Rate_Constants(object):
    """Holds all rate constants currently associated with the model.
    To inspect the expression and current settings of it you can just
    call it as a function with a (glob) pattern that matches
    the desired processes, e.g. ::

      model.rate_constant('*ads*')

    could print all rate constants for adsorption. Given of course that
    'ads' is part of the process name. The just get the rate constant
    for one specific process you can use ::

      model.rate_constant.by_name("<process name>")

    To set rate constants manually use ::

      model.rate_constants.set("<pattern>", <rate-constant (expr.)>)

    """

    def __repr__(self):
        """Compact representation of all current rate_constants."""
        res = '# kMC rate constants (%i)\n' % len(settings.rate_constants)
        res += '# ------------------\n'
        for i, proc in enumerate(sorted(settings.rate_constants)):
            rate_expr = settings.rate_constants[proc][0]
            rate_const = base.get_rate(i + 1)
            res += '# %s: %s = %.2e s^{-1}\n' % (proc, rate_expr, rate_const)
        res += '# ------------------\n'

        return res

    def __call__(self, pattern=None):
        """Return rate constants.

        :param pattern: fname pattern to filter matching parameter name.
        :type pattern: str

        """
        res = ''
        for i, proc in enumerate(sorted(settings.rate_constants.keys())):
            if pattern is None or fnmatch(proc, pattern):
                rate_expr = settings.rate_constants[proc][0]
                rate_const = evaluate_rate_expression(rate_expr,
                                                      settings.parameters)
                res += ('# %s: %s = %.2e s^{-1}\n' % (proc, rate_expr,
                                                      rate_const))
        if INTERACTIVE:
            print(res)
        else:
            return res

    def names(self, pattern=None):
        """Return names of processes that match `pattern`.

        :param pattern: fname pattern to filter matching parameter name.
        :type pattern: str

        """
        names = []
        for i, proc in enumerate(sorted(settings.rate_constants.keys())):
            if pattern is None or fnmatch(proc, pattern):
                names.append(proc)
        return names

    def by_name(self, proc):
        """Return rate constant currently set for `proc`

        :param proc: Name of process.
        :type proc: str
        """
        rate_expr = settings.rate_constants[proc][0]
        return evaluate_rate_expression(rate_expr, settings.parameters)

    def inverse(self):
        """Return inverse list of rate constants.

        """
        res = '# kMC rate constants (%i)\n' % len(settings.rate_constants)
        res += '# ------------------\n'
        for proc in sorted(settings.rate_constants):
            rate_expr = settings.rate_constants[proc][0]
            rate_const = evaluate_rate_expression(rate_expr,
                                                  settings.parameters)
            res += '# %s: %.2e s^{-1} = %s\n' % (proc, rate_const, rate_expr)
        res += '# ------------------\n'
        if INTERACTIVE:
            print(res)
        else:
            return res

    def set(self, pattern, rate_constant, parameters=None):
        """Set rate constants. Pattern can be a glob pattern,
        and the rate constant will be applied to all processes,
        where the pattern matches. The rate constant can be either
        a number or a rate expression.

        :param pattern: fname pattern that selects the process affected.
        :type pattern: str
        :param rate_constant: Rate constant to be set.
        :type rate_constant: str or float
        :param parameters: List of parameters to be used when
                           evaluating expression.
        :type parameters: list

        """

        if parameters is None:
            parameters = settings.parameters
        if type(rate_constant) is str:
            rate_constant = evaluate_rate_expression(rate_constant,
                                                     parameters)
        try:
            rate_constant = float(rate_constant)
        except:
            raise UserWarning("Could not convert rate constant to float")
        for i, proc in enumerate(sorted(settings.rate_constants.keys())):
            if pattern is None or fnmatch(proc, pattern):
                base.set_rate_const(i + 1, rate_constant)


class ModelParameter(object):
    """A model parameter to be scanned. If instantiated with only
    one value this parameter will be fixed at this value.

    Use a subclass for specific type of grid.

    :param min: Minimum value for this parameter.
    :type min: float
    :param max: Maximum value for this parameter (Default: min)
    :type max: float
    :param steps: Number of steps between minimum and maximum.
    :type steps: int

    """

    def __init__(self, min, max=None, steps=1, type=None, unit=''):
        self.min = min
        self.max = max if max is not None else min
        self.steps = steps
        self.type = type
        self.unit = unit

    def __repr__(self):
        return ('[%s] min: %s, max: %s, steps: %s'
              % (self.type, self.min, self.max, self.steps))

    def get_grid(self):
        pass


class PressureParameter(ModelParameter):
    """Create a grid of p \in [p_min, p_max] such
    that ln({p}) is a regular grid.

    """

    def __init__(self, *args, **kwargs):
        kwargs['type'] = 'pressure'
        kwargs['unit'] = 'bar'
        super(PressureParameter, self).__init__(*args, **kwargs)

    def get_grid(self):
        from kmos.utils import p_grid
        return p_grid(self.min, self.max, self.steps)


class TemperatureParameter(ModelParameter):
    """Create a grid of p \in [T_min, T_max] such
    that ({T})**(-1) is a regular grid.

    """

    def __init__(self, *args, **kwargs):
        kwargs['type'] = 'temperature'
        kwargs['unit'] = 'K'
        super(TemperatureParameter, self).__init__(*args, **kwargs)

    def get_grid(self):
        from kmos.utils import T_grid
        return T_grid(self.min, self.max, self.steps)


class LogParameter(ModelParameter):
    """Create a log grid  between 10^min and 10^max
    (like np.logspace)

    """

    def __init__(self, *args, **kwargs):
        kwargs['type'] = 'log'
        super(LogParameter, self).__init__(*args, **kwargs)

    def get_grid(self):
        return np.logspace(self.min, self.max, self.steps)


class LinearParameter(ModelParameter):
    """Create a regular grid between min and max.

    """

    def __init__(self, *args, **kwargs):
        kwargs['type'] = 'linear'
        super(LinearParameter, self).__init__(*args, **kwargs)

    def get_grid(self):
        return np.linspace(self.min, self.max, self.steps)


class _ModelRunner(type):

    def __new__(cls, name, bases, dct):
        obj = super(_ModelRunner, cls).__new__(cls, name, bases, dct)
        obj.runner_name = name
        obj.parameters = OrderedDict()
        for key, item in dct.items():
            if key == '__module__':
                pass
            elif isinstance(item, ModelParameter):
                obj.parameters[key] = item

        return obj


class ModelRunner(object):
    """
Setup and initiate many runs in parallel over a regular grid
of parameters. A standard type of script is given below.

To allow execution from multiple hosts connected
to the same filesystem calculated points are blocked
via <classname>.lock. To redo a calculation <classname>.dat
and <classname>.lock should be moved out of the way ::

    from kmos.run import ModelRunner, PressureParameter, TemperatureParameter


    class ScanKinetics(ModelRunner):
        p_O2gas = PressureParameter(1)
        T = TemperatureParameter(600)
        p_COgas = PressureParameter(min=1, max=10, steps=40)
        # ... other parameters to scan


    ScanKinetics().run(init_steps=1e7, sample_steps=1e7, cores=4)

    """

    __metaclass__ = _ModelRunner

    def __product(self, *args, **kwds):
        """Manual implementation of itertools.product for
          python <= 2.5 """

        # product('ABCD', 'xy') --> Ax Ay Bx By Cx Cy Dx Dy
        # product(range(2), repeat=3) --> 000 001 010 011 100 101 110 111
        pools = map(tuple, args) * kwds.get('repeat', 1)
        result = [[]]
        for pool in pools:
            result = [x + [y] for x in result for y in pool]
        for prod in result:
            yield tuple(prod)

    def __split_seq(self, seq, size):
        """Split a list into n chunks of roughly equal size."""
        newseq = []
        splitsize = 1.0 / size * len(seq)
        for i in range(size):
                newseq.append(seq[int(round(i * splitsize)):
                                  int(round((i + 1) * splitsize))])
        return newseq

    def __touch(self, fname, times=None):
        """Pythonic version of Unix touch.

        :param fname: filename.
        :type fname: str
        :param times: timestamp (Default: None meaning now).
        :type times: datetime timestamp

        """
        fhandle = file(fname, 'a')
        try:
            os.utime(fname, times)
        finally:
            fhandle.close()

    def __run_sublist(self, sublist, init_steps, sample_steps, samples, random_seed=None):
        """
        Run sampling run for a list of parameter-tuples.

        :param init_steps: Steps to run model before sampling (.ie. to reach steady-state).
        :type init_steps: int
        :param sample_steps: Number of steps to sample over.
        :type sample_steps: int
        :param cores: Number of parallel processes to launch.
        :type cores: int
        :param samples: Number of samples. Use more samples if precise coverages are needed.
        :type samples: int

        """
        for i, datapoint in enumerate(sublist):
            #============================
            # DEFINE labels
            #===========================
            lockfile = '%s.lock' % (self.runner_name)
            format_string = '_'.join(['%s'] * (len(self.parameters) + 1))
            arguments = tuple([self.runner_name] + list(datapoint))

            input_line = format_string % arguments

            outfile = os.path.abspath('%s.dat' % (self.runner_name))


            #============================
            # lockfile mechanism
            #===========================
            self.__touch(lockfile)
            fdata = file(lockfile)
            readlines = map(lambda x: x.strip(), fdata.readlines())
            fdata.close()
            if input_line in readlines:
                continue
            fdata = file(lockfile, 'a')
            fdata.write('%s\n' % input_line)
            fdata.close()

            #============================
            # SETUP Model
            #===========================
            model = KMC_Model(print_rates=False,
                              banner=False,
                              random_seed=random_seed,
                              cache_file='%s_configs/config_%s.pckl'
                                          % (self.runner_name, input_line))
            for name, value in zip(self.parameters.keys(), datapoint):
                setattr(model.parameters, name, value)

            #============================
            # EVALUATE model
            #===========================
            model.do_steps(int(init_steps))
            data = model.get_std_sampled_data(samples=samples,
                                              sample_size=int(sample_steps),
                                              tof_method='integ')

            if not os.path.exists(outfile):
                out = file(outfile, 'a')
                out.write(model.get_std_header())
                out.write(str(model.parameters))
                out.write("""# If one or more parameters change between data lines\n# the set above corresponds to the first line.\n""")
                out.close()
            out = file(outfile, 'a')
            out.write(data)
            out.close()
            model.deallocate()

    def plot(self,
             rcParams=None,
             touchup=None,
             filename=None,
             backend='Agg',
             suffixes=['png', 'pdf', 'eps'],
             variable_parameters=None,
             fig_width_pt=246.0,
             plot_tofs=None,
             plot_occs=None,
             occ_xlabel=None,
             occ_ylabel=None,
             tof_xlabel=None,
             tof_ylabel=None,
             label=None,
             sublabel=None,
             arrhenius=False,
             ):
        """
        Plot the generated data using matplotlib. By default we will try
        to generate publication quality output of the specified TOFs and
        coverages.
        """
        import matplotlib
        matplotlib.use(backend, warn=False)
        # Suppress backend warning, because we cannot
        # control how often the current method is called from
        # a script and superfluous warning tends to confuse users
        from matplotlib import pyplot as plt


        inches_per_pt = 1.0 / 72.27               # Convert pt to inches
        golden_mean = (np.sqrt(5)-1.0) / 2.0         # Aesthetic ratio
        fig_width = fig_width_pt * inches_per_pt  # width in inches
        fig_height = fig_width * golden_mean       # height in inches
        figsize = [fig_width, fig_height]
        font_size = 10
        tick_font_size = 8
        xlabel_pad = 6
        ylabel_pad = 16

        default_rcParams = {
            'font.family': 'serif',
            'font.serif': 'Computer Modern Roman',
            'font.sans-serif': 'Computer Modern Sans serif',
            'font.size': 10,
            'axes.labelsize': font_size,
            'legend.fontsize': font_size,
            'xtick.labelsize': tick_font_size,
            'ytick.labelsize': tick_font_size,
            'text.usetex': 'false',
            'lines.linewidth': 1.,
        }

        data = np.recfromtxt('%s.dat' % self.runner_name, names=True, deletechars=None)

        model = KMC_Model(print_rates=False,
                          banner=False,)

        # override with user-provided parameters
        if rcParams is not None:
            default_rcParams.update(rcParams)
        matplotlib.rcParams.update(default_rcParams)

        # plot all TOFs defined in model if not specified
        if plot_tofs is None:
            plot_tofs = model.tofs

        if plot_occs is None:
            plot_occs = list(data.dtype.names)
            plot_occs.remove('kmc_time')
            plot_occs.remove('kmc_steps')
            for header_param in model.get_param_header().split():
                plot_occs.remove(header_param)

            for tof in model.tofs:
                tof = tof.replace(')', '').replace('(', '')
                try:
                    plot_occs.remove(tof)
                except ValueError:
                    print('%s not in %s' % (tof, plot_occs))

        # check how many variable parameters we have
        # if not specified

        if variable_parameters is None:
            variable_parameters = {}
            for param_name, param in self.parameters.items():
                if param.steps > 1:
                    variable_parameters[param_name] = param
        else:
            vparams = {}
            for vparam in variable_parameters:
                if vparam in self.parameters:
                    vparams[vparam] = self.parameters[vparam]
                else:
                    raise UserWarning("Request variable not in ModelRunner.")

            variable_parameters = vparams



        ######################
        # plot coverages     #
        ######################
        fig = plt.figure(figsize=figsize)
        if len(variable_parameters) == 0:
            print("No variable parameter. Nothing to plot.")
        elif len(variable_parameters) == 1:
            xvar = variable_parameters.keys()[0]
            data.sort(order=xvar)
            for occ in plot_occs:
                occs = [data[name] for name in data.dtype.names if name.startswith(occ)]
                N_occs = len(occs)
                occ_data = np.array(occs).sum(axis=0) / N_occs
                plt.plot(data[xvar], occ_data, label=occ.replace('_', '\_'))
            legend = plt.legend(loc='best', fancybox=True)
            legend.get_frame().set_alpha(0.5)
            plt.ylim([0, 1])


        elif len(variable_parameters) == 2:
            print("Two variable parameters. Doing a surface plot.")
        else:
            print("Too many variable parameters. No automatic plotting possible.")

        for suffix in suffixes:
            if label is None:
                if sublabel is None:
                    plt.savefig('%s_coverages.%s' % (self.runner_name, suffix), bbox_inces='tight')
                else:
                    plt.savefig('%s_%s_coverages.%s' % (self.runner_name, sublabel, suffix), bbox_inces='tight')
            else:
                if sublabel is None:
                    plt.savefig('%s_coverages.%s' % (label, suffix), bbox_inces='tight')
                else:
                    plt.savefig('%s_%s_coverages.%s' % (label, sublabel, suffix), bbox_inces='tight')


        ######################
        # plot TOFs          #
        ######################
        fig = plt.figure(figsize=figsize)
        if len(variable_parameters) == 0:
            print("No variable parameter. Nothing to plot.")
        elif len(variable_parameters) == 1:
            xvar = variable_parameters.keys()[0]
            param = variable_parameters.values()[0]
            data.sort(order=xvar)
            for tof in plot_tofs:
                tof = tof.replace(')', '').replace('(', '')
                if arrhenius :
                    plt.plot(1000./data[xvar], np.log(data[tof]), label=tof.replace('_', '\_'))
                else:
                    plt.plot(data[xvar], data[tof], label=tof.replace('_', '\_'))
            legend = plt.legend(loc='best', fancybox=True)
            legend.get_frame().set_alpha(0.5)
            if arrhenius:
                plt.xlabel(r'$1000\,/%s$ [%s$^{-1}$]' % (xvar, param.unit))
                plt.ylabel(r'log(TOF)')
            else:
                plt.xlabel(r'\emph{%s} [%s]' % (xvar, param.unit))
                plt.ylabel(r'TOF [s$^{-1}$ cell$^{-1}$]')
        elif len(variable_parameters) == 2:
            print("Two variable parameters. Doing a surface plot.")
        else:
            print("Too many variable parameters. No automatic plotting possible.")

        for suffix in suffixes:
            if label is None:
                plt.savefig('%s_TOFs.%s' % (self.runner_name, suffix), bbox_inches='tight')
            else:
                plt.savefig('%s_TOFs.%s' % (label, suffix), bbox_inches='tight')

        model.deallocate()

    def run(self, init_steps=1e8,
                  sample_steps=1e8,
                  cores=4,
                  samples=1,
                  random_seed=None):
        """Launch the ModelRunner instance. Creates a regular grid over
        all ModelParameters defined in the ModelRunner class.

        :param init_steps: Steps to run model before sampling (.ie. to reach steady-state).
        (Default: 1e8)
        :type init_steps: int
        :param sample_steps: Number of steps to sample over (Default: 1e8)
        :type sample_steps: int
        :param cores: Number of parallel processes to launch.
        :type cores: int
        :param samples: Number of samples. Use more samples if precise coverages are needed (Default: 1).
        :type samples: int

        """

        parameters = []
        for parameter in self.parameters.values():
            parameters.append(parameter.get_grid())
        points = list(self.__product(*tuple(parameters)))

        random.shuffle(points)

        for sub_list in self.__split_seq(points, cores):
            p = Process(target=self.__run_sublist, args=(sub_list,
                                                         init_steps,
                                                         sample_steps,
                                                         samples,
                                                         random_seed,
                                                         ))
            p.start()


def set_rate_constants(parameters=None, print_rates=None):
    """Tries to evaluate the supplied expression for a rate constant
    to a simple real number and sets it for the corresponding process.
    For the evaluation it draws on predefined natural constants, user defined
    parameters and mathematical functions.

    :param parameters: List of parameters to be used when evaluating expression.
                      (Default: None)
    :type parameters: list
    :param print_rates: Print the rates while setting them
                        (Default: True)
    :type print_rates: bool

    """
    proclist = ProclistProxy()
    if print_rates is None:
        print_rates = True

    if parameters is None:
        parameters = settings.parameters

    if print_rates:
        print('-------------------')
    for proc in sorted(settings.rate_constants):
        rate_expr = settings.rate_constants[proc][0]
        rate_const = evaluate_rate_expression(rate_expr, parameters)

        if rate_const < 0.:
            raise UserWarning('%s = %s: Negative rate-constants do no make sense'
                              % (rate_expr, rate_const))
        try:
            base.set_rate_const(getattr(proclist, proc.lower()),
                                rate_const)
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
    """Wrapper for import ASE."""
    try:
        import ase
        import ase.visualize
    except:
        print('Please download the ASE from')
        print('https://wiki.fysik.dtu.dk/ase/')
    return ase


def get_tof_names():
    """Return names turn-over-frequencies (TOF) previously defined in model."""
    tofs = []
    for process, tof_count in settings.tof_count.iteritems():
        for tof in tof_count:
            if tof not in tofs:
                tofs.append(tof)
    return sorted(tofs)


class ProcInt(int):

    def __new__(cls, value, *args, **kwargs):
        return int.__new__(cls, value)

    def __init__(self, value):
        self.procnames = sorted(settings.rate_constants.keys())

    def __repr__(self):
        name = self.procnames[self.__int__() - 1]
        return 'Process model.proclist.%s (%s)' % (name.lower(), self.__int__())


class SiteInt(int):

    def __new__(cls, value, *args, **kwargs):
        return int.__new__(cls, value)

    def __repr__(self):
        x, y, z, n = lattice.calculate_nr2lattice(self.__int__())
        return 'Site (%s, %s, %s, %s) [#%s]' % (x, y, z, n, self.__int__())

    def __getitem__(self, item):
        site = lattice.calculate_nr2lattice(self.__int__())
        return site[item]
