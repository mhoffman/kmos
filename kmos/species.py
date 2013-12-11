#!/usr/bin/env python
"""Very simple module that keeps several species
commonly needed to model heterogeneous catalyst kinetics
"""
#    Copyright 2009-2013 Max J. Hoffmann (mjhoffmann@gmail.com)
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
from numpy import interp as interp1d
from math import log
import os

janaf_data = None
try:
    import janaf_data
except:
    raise Exception("""
    Error: Could not import JANAF data
    Installing JANAF Thermochemical Tables
    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    You can conveniently use gas phase chemical potentials
    inserted in rate constant expressions using
    JANAF Thermochemical Tables. A couple of molecules
    are automatically supported. If you need support
    for more gas-phase species, drop me a line.

    The tabulated values are not distributed since
    the terms of distribution do not permit this.
    Fortunately manual installation is easy.
    Just create a directory called `janaf_data`
    anywhere on your python path. To see the directories on your python
    path run ::

        python -c"import sys; print(sys.path)"

        Inside the `janaf_data` directory has to be a file
        named `__init__.py`, so that python recognizes it as a module ::

            touch __init__.py

            Then copy all needed data files from the
            `NIST website <http://kinetics.nist.gov/janaf/Search>`_
            in the tab-delimited text format
            to the `janaf_data` directory.""")


class Species(object):
    def __init__(self, atoms, gas=False, janaf_file='', name=''):
        self.atoms = atoms
        self.gas = gas
        if name:
            self.name = name
        else:
            if hasattr(self.atoms, 'get_chemical_formula'):
                self.name = self.atoms.get_chemical_formula(mode='hill')
            else:
                self.atoms.get_name()
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
                val = interp1d(T, self.T_grid, self.G_grid) + \
                       kboltzmann_in_eVK * T * log(p)
            except Exception:
                raise Exception('Could not find JANAF tables for %s.'
                                % self.name)
            else:
                return val

        else:
            raise UserWarning('%s is no gas-phase species.' % self.name)

    def _prepare_G_p0(self, filename):
        # from CODATA 2010
        Jmol_in_eV = 1.03642E-5
        # load data
        try:
            data = np.loadtxt(filename, skiprows=2, usecols=(0, 2, 4))
        except IOError:
            print('Warning: JANAF table %s not installed' % filename)
            return

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

HClgas = Species(ase.atoms.Atoms(),
                 gas=True,
                 janaf_file='Cl-026.txt',
                 name='HClgas')

Cl2gas = Species(ase.atoms.Atoms(),
                 gas=True,
                 janaf_file='Cl-073.txt',
                 name='Cl2gas',)

H2Ogas = Species(ase.atoms.Atoms(),
                 gas=True,
                 janaf_file='H-064.txt',
                 name='H2Ogas',)

H2Oliquid = Species(ase.atoms.Atoms(),
                    gas=False,
                    janaf_file='H-063.txt',
                    name='H2Oliquid',)

