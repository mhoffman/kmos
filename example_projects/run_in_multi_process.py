#!/usr/bin/env python
"""Example run script for kMC Model

WARNING: The values chosen for convergence, model size and
sampling are most likely incorrect for your model.
Please check very carefully for convergence and
good sampling.

"""

import os
from multiprocessing import Pool

import numpy as np

import kmc_settings
from kmos.run import KMC_Model

DATA_FILENAME = 'data.dat'
INITIAL_STEPS = int(1e5)
SAMPLES = 1000
BETWEEN_SAMPLES = 10
INITIAL_TIME = 5e-7


def run(point):
    """Run function"""
    T, p_COgas, p_O2gas = point
    kmc_settings.simulation_size = 1
    with KMC_Model(print_rates=False, banner=False) as model:
        # Write header to data file
        if not os.path.isfile(DATA_FILENAME):
            with file(DATA_FILENAME, 'w') as datafile:
                datafile.write("#T p_CO p_O2 kmc_time %s %s\n"
                               % (model.get_tof_header(),
                                  model.get_occupation_header()))
                datafile.write(str(model))

        # Set experimental parameters
        model.parameters.p_COgas = p_COgas
        model.parameters.p_O2gas = p_O2gas
        model.parameters.T = T

        # Run simulation
        last_time = 0.
        for double_step in xrange(3):
            last_time = model.base.get_kmc_time()
            model.double()
            model.base.set_kmc_time(last_time)
            print(model.size)
            while not model.base.get_kmc_time() > INITIAL_TIME + last_time:
                model.do_steps(INITIAL_STEPS)

        atoms = model.get_atoms(geometry=False)
        occupation = []
        tof = []
        delta_ts = []
        for i in xrange(SAMPLES):
            model.do_steps()
            atoms = model.get_atoms(geometry=False)

            occupation.append(atoms.occupation.flatten())
            tof.append(atoms.tof_data)
            delta_ts.append(atoms.delta_t)
        occupation = np.average(occupation, axis=0, weights=delta_ts)
        tof = np.average(tof, axis=0, weights=delta_ts)

        kmc_time = sum(delta_ts)
        with file(DATA_FILENAME, 'a') as datafile:
            outdata = tuple([T, p_COgas, p_O2gas, kmc_time]
							 + list(tof)
                             + list(occupation))
            datafile.write((' '.join(['%.3e'] * len(outdata)) + '\n')
                            % outdata)

if __name__ == '__main__':
    p_COgas = np.logspace(-5, 3, 9)
    T = [600] * len(p_COgas)
    p_O2gas = [1.] * len(p_COgas)
    nproc = 8
    pool = Pool(processes=nproc)
    pool.map(run, zip(T, p_COgas, p_O2gas))
