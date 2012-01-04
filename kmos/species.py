#!/usr/bin/env python
"""Very simple module that keeps several species
commonly needed to model heterogeneous catalyst kinetics
"""
#    Copyright 2009-2012 Max J. Hoffmann (mjhoffmann@gmail.com)
#    This file is part of kmos.

#    kmos is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    kmos is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with kmos.  If not, see <http://www.gnu.org/licenses/>.

import ase
import numpy as np
from scipy.interpolate import interp1d
from math import log
import re
import os
try:
    import janaf_data
except:
    janaf_data = None


class Species:
    def __init__(self, atoms, gas=False, janaf_file='', name=''):
        self.atoms = atoms
        self.gas = gas
        self.name = name if name else self.atoms.get_name()
        self.janaf_file = janaf_file

        # prepare chemical potential
        if self.gas and self.janaf_file and janaf_data is not None:
            self._prepare_G_p0(
                os.path.abspath(os.path.join(
                janaf_data.__path__[0],
                self.janaf_file)))

    def __repr__(self):
        return self.name

    def mu(self, T, p):
        """Expecting T in Kelvin, p in bar"""
        if self.gas:
            kboltzmann_in_eVK = 8.6173324e-5
            # interpolate given grid
            try:
                val =  interp1d(self.T_grid, self.G_grid)(T) + \
                       kboltzmann_in_eVK * T * log(p)
            except Exception, e:
                print('Possibly forgot to intall JANAF tables?')
                raise
            else:
                return val

        else:
            raise UserWarning('%s is no gas-phase species.' % self.name)

    def _prepare_G_p0(self, filename):
        # from CODATA 2010
        Jmol_in_eV = 1.03642E-5
        # load data
        data = np.loadtxt(filename, skiprows=2, usecols=(0, 2, 4))

        # define data
        self.T_grid = data[:, 0]
        self.G_grid = (1000 * (data[:, 2] - data[0, 2])
                               - data[:, 0] * data[:, 1]) * Jmol_in_eV

    def __eq__(self, other):
        return self.atoms == other.atoms and self.gas == other.gas

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return id(self)

    # Currently not used
    def _generate_mu_estimate(self, molecule):
        """This function estimates mu, the gas phase chemical potential
        based on the translational and the rotational contributions
        to the gas phase entropy.
        Derivations can be found in e.g. Pathria, Statistical mechanics,
        Elsevier, 2001, ISBN 978-7-5062-6017-6

        # TODO: vibrational contribution
        # TODO: ASE does not seems to support eigenmode calculation
        # for molecules of more than 2 atoms
        """

        # Optimize geometry first
        bfgs = ase.optimize.bfgs.BFGS(molecule)
        bfgs.run()

        I = moments_of_inertia = molecule.get_moments_of_inertia()
        m = sum(molecule.get_masses()) * cs.u

        # prefactor
        def pref(T):
            return cs.k * T / cs.elementary_charge

        # calculate translational partition function
        # only depends on total mass
        def qtrans(T, p):
            return (2 * np.pi * m / \
                    ((1 / (cs.k * T)) * cs.h ** 2)) ** (3. / 2) * 1 / \
                    ((1 / (cs.k * T)) * p * cs.bar)

        # Calculate rotational contribution
        # depends on moments of inertia and
        # assumes different formulae if some
        # elements vanish.
        # Calculating classical contributions only.
        nonzero_moments = map(lambda x: x > 10.e-7, moments_of_inertia)
        nonzero_moments = nonzero_moments.count(True)
        if nonzero_moments == 3:
            sqrtI = np.sqrt(
                np.product(
                    moments_of_inertia) * (cs.u * cs.angstrom ** 2) ** 3)

            def qrot(T):
                return np.sqrt(np.pi) * sqrtI * (8 * np.pi ** 2 /
                                  ((1 / (cs.k * T)) * cs.h ** 2)) ** (3. / 2)

        elif nonzero_moments == 2:
            # If molecule has reflection symmetry along
            # axis of zero moment of inertia we need
            # to divide by a factor of 2. to avoid double
            # counting of phase space.
            if eval(get_spacegroup(molecule).split()[1]) == 123:
                sigma = 1
            else:
                sigma = 2

            def qrot(T):
                return 8 * np.pi ** 2 * I[0] * cs.u * cs.angstrom ** 2 / \
                    (sigma * (1 / (cs.k * T)) * cs.h ** 2)
        else:

            def qrot(T):
                return 1.

        qvibstr = '1'

        a = []
        b = []
        # remove *.pckl file from previous calculation
        # or ASE will try to reuse the wrong files
        for vibpckl in glob('vib*pckl'):
            os.remove(vibpckl)
        if len(molecule) > 3:
            vib = Vibrations(molecule)
            vib.run()
            frequencies = filter(lambda x: x > 20,
                                 np.real(vib.get_frequencies()))
            for nu in frequencies:
                qvibstr += ('*(np.exp(-cs.c*cs.h*%s/(2*cs.k*T))/ '
                            + '(1-np.exp(-cs.c*cs.h*%s/(cs.k*T))))') % (nu, nu)

        def qvib(T):
            return eval(qvibstr)

        # qvib does not seem to be accurate for bad potentials
        def qvib(T):
            return 1.

        def mu(T, p):
            return -pref(T) * np.log(qtrans(T, p) * qrot(T) * qvib(T))
        return mu


# prepare all required species
H2gas = Species(ase.atoms.Atoms('H2', [[0, 0, 0], [0, 0, 1.2]],),
    gas=True,
    janaf_file='H-050.txt',
    name='H2gas')

H = Species(ase.atoms.Atoms('H'))

CH4gas = Species(ase.atoms.Atoms('CH4',
     [[-2.14262, 3.03116, 0.00000],
     [-1.07262, 3.03116, 0.00000],
     [-2.49979, 4.03979, 0.00000],
     [-2.51306, 2.50700, 0.85611],
     [-2.49435, 2.53348, -0.87948]],
     ), gas=True,
     janaf_file='C-067.txt',
     name='CH4gas')
CH4 = Species(ase.atoms.Atoms('CH4',
     [[-2.14262, 3.03116, 0.00000],
     [-1.07262, 3.03116, 0.00000],
     [-2.49979, 4.03979, 0.00000],
     [-2.51306, 2.50700, 0.85611],
     [-2.49435, 2.53348, -0.87948]],
     ),
     name='CH4')
O = Species(ase.atoms.Atoms('O',
    [[0, 0, 0]],
    cell=[10, 10, 10],
    ),
    name='O')
O2gas = Species(ase.atoms.Atoms('O2',
    [[0, 0, 0],
    [0, 0, 1.2]],
    cell=[10, 10, 10],
    ),
    gas=True,
    janaf_file='O-029.txt',
    name='O2gas')

NOgas = Species(ase.atoms.Atoms('NO',
    [[0, 0, 0], [0, 0, 1.2]],
    cell=[10, 10, 10],
    ),
    gas=True,
    janaf_file='N-005.txt',
    name='NOgas',
    )

NO = Species(ase.atoms.Atoms('NO', [[0, 0, 0], [0, 0, 1.2]],
                             cell=[10, 10, 10], ),
                name='NO',
                janaf_file='N-005.txt',
    )

NO2gas = Species(ase.atoms.Atoms(),
                 gas=True,
                 janaf_file='N-007.txt',
                 name='NO2gas')

NO3gas = Species(ase.atoms.Atoms(),
                 gas=True,
                 janaf_file='N-009.txt',
                 name='NO3gas')

COgas = Species(ase.atoms.Atoms('CO', [[0, 0, 0], [0, 0, 1.2]],
                                cell=[10, 10, 10],),
    gas=True,
    janaf_file='C-093.txt',
    name='COgas')
CO = Species(ase.atoms.Atoms('CO', [[0, 0, 0], [0, 0, 1.2]],
                             cell=[10, 10, 10], ),
    name='CO')

CO2gas = Species(ase.atoms.Atoms('CO2',
    [[0, 0, -1.2],
     [0, 0, 0],
     [0, 0, 1.2]],
     cell=[10, 10, 10],
     ),
     gas=True,
     janaf_file='C-095.txt',
     name='CO2gas')

NH3gas = Species(ase.atoms.Atoms(symbols='NH3',
          pbc=np.array([True,  True,  True], dtype=bool),
          cell=np.array(
      [[10.,   0.,   0.],
       [0.,  10.,   0.],
       [0.,   0.,  10.]]),
          positions=np.array(
      [[0.13288865,  0.13288865,  0.13288865],
       [-0.03325795, -0.03325795,  1.13361278],
       [-0.03325795,  1.13361278, -0.03325795],
       [1.13361278, -0.03325795, -0.03325795]])),
      gas=True,
      janaf_file='H-083.txt',
      name='NH3gas')

C2H4gas = Species(ase.atoms.Atoms(),
                  gas=True,
                  janaf_file='C-128.txt',
                  name='C2H4gas')
