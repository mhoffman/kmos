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
import sys

# List of all supported JANAF data files
SUPPORTED_JANAF_FILES = [
    "C-067.txt",  # CO2
    "C-093.txt",  # CH4
    "C-095.txt",  # CO
    "C-128.txt",  # CH3OH
    "Cl-026.txt",  # Cl2
    "Cl-073.txt",  # HCl
    "H-050.txt",  # H2
    "H-063.txt",  # H2O2
    "H-064.txt",  # HNO3
    "H-083.txt",  # H2O
    "N-005.txt",  # N2
    "N-007.txt",  # NH3
    "N-009.txt",  # NO
    "O-029.txt",  # O2
]


def download_janaf_data():
    """Download all supported JANAF data files from NIST website."""
    import urllib.request

    # Create janaf_data directory in user's home directory (~/.kmos/janaf_data)
    kmos_dir = os.path.expanduser("~/.kmos")
    janaf_dir = os.path.join(kmos_dir, "janaf_data")

    if not os.path.exists(janaf_dir):
        os.makedirs(janaf_dir)
        print(f"Created directory: {janaf_dir}")

    # Create __init__.py to make it a Python module
    init_file = os.path.join(janaf_dir, "__init__.py")
    if not os.path.exists(init_file):
        with open(init_file, "w") as f:
            f.write("# JANAF Thermochemical Tables data directory\n")
        print(f"Created {init_file}")

    # Download each file
    base_url = "https://janaf.nist.gov/tables/"
    success_count = 0

    for filename in SUPPORTED_JANAF_FILES:
        filepath = os.path.join(janaf_dir, filename)

        # Skip if file already exists
        if os.path.exists(filepath):
            print(f"  {filename} (already exists)")
            success_count += 1
            continue

        url = base_url + filename
        try:
            print(f"  Downloading {filename}...", end=" ")
            urllib.request.urlretrieve(url, filepath)
            print("done")
            success_count += 1
        except Exception as e:
            print(f"failed (Error: {e})")

    print(
        f"\nDownloaded {success_count}/{len(SUPPORTED_JANAF_FILES)} JANAF data files to {janaf_dir}"
    )

    # Add .kmos directory to sys.path if not already there
    if kmos_dir not in sys.path:
        sys.path.insert(0, kmos_dir)

    return janaf_dir


janaf_data = None

# Add ~/.kmos to sys.path to find janaf_data
kmos_dir = os.path.expanduser("~/.kmos")
if os.path.exists(kmos_dir) and kmos_dir not in sys.path:
    sys.path.insert(0, kmos_dir)

try:
    import janaf_data
except ImportError:
    # Ask user if they want to download JANAF data automatically
    print("""
    Error: Could not import JANAF data

    JANAF Thermochemical Tables are needed for gas phase chemical potentials.
    The data files can be automatically downloaded from the NIST website.
    """)

    response = (
        input("Would you like to download JANAF data now? [Y/n]: ").strip().lower()
    )

    if response in ["", "y", "yes"]:
        print("\nDownloading JANAF Thermochemical Tables...")
        try:
            janaf_dir = download_janaf_data()
            # Try to import again
            import janaf_data

            print("\nJANAF data successfully installed!")
        except Exception as e:
            print(f"\nFailed to download JANAF data: {e}")
            print(
                """
    Manual Installation
    ^^^^^^^^^^^^^^^^^^^

    You can manually install JANAF data by:
    1. Creating a directory: mkdir -p ~/.kmos/janaf_data
    2. Creating an __init__.py file inside: touch ~/.kmos/janaf_data/__init__.py
    3. Downloading data files from https://janaf.nist.gov/tables/
       (Files needed: {})
    """.format(", ".join(SUPPORTED_JANAF_FILES))
            )
    else:
        print(
            """
    Skipping JANAF data download.

    Note: You can manually install JANAF data later by:
    1. Creating a directory: mkdir -p ~/.kmos/janaf_data
    2. Creating an __init__.py file inside: touch ~/.kmos/janaf_data/__init__.py
    3. Downloading data files from https://janaf.nist.gov/tables/
       (Files needed: {})
    """.format(", ".join(SUPPORTED_JANAF_FILES))
        )


class Species(object):
    def __init__(self, atoms, gas=False, janaf_file="", name=""):
        self.atoms = atoms
        self.gas = gas
        if name:
            self.name = name
        else:
            if hasattr(self.atoms, "get_chemical_formula"):
                self.name = self.atoms.get_chemical_formula(mode="hill")
            else:
                self.atoms.get_name()
        self.janaf_file = janaf_file

        # prepare chemical potential
        if self.gas and self.janaf_file and janaf_data is not None:
            self._prepare_G_p0(
                os.path.abspath(os.path.join(janaf_data.__path__[0], self.janaf_file))
            )

    def __repr__(self):
        return self.name

    def mu(self, T, p):
        """Expecting T in Kelvin, p in bar"""
        if self.gas:
            kboltzmann_in_eVK = 8.6173324e-5
            # Check if JANAF data was loaded
            if not hasattr(self, "T_grid") or not hasattr(self, "G_grid"):
                raise Exception(
                    f"JANAF thermochemical data not available for {self.name}. "
                    f"The required JANAF table file could not be loaded or downloaded. "
                    f'Please check if the file "{self.janaf_file}" is available or can be downloaded.'
                )
            # interpolate given grid
            try:
                val = interp1d(
                    T, self.T_grid, self.G_grid
                ) + kboltzmann_in_eVK * T * log(p)
            except Exception as e:
                raise Exception(
                    f"Could not interpolate JANAF data for {self.name} at T={T}K, p={p}bar. "
                    f"Error: {e}"
                )
            else:
                return val

        else:
            raise UserWarning("%s is no gas-phase species." % self.name)

    def _prepare_G_p0(self, filename):
        # from CODATA 2010
        Jmol_in_eV = 1.03642e-5
        # load data
        try:
            data = np.loadtxt(filename, skiprows=2, usecols=(0, 2, 4))
        except IOError:
            # Try to download the missing JANAF file
            print(
                f"Warning: JANAF table {filename} not found, attempting to download..."
            )
            janaf_filename = os.path.basename(filename)

            if self._download_single_janaf_file(janaf_filename, filename):
                # Retry loading after download
                try:
                    data = np.loadtxt(filename, skiprows=2, usecols=(0, 2, 4))
                except IOError:
                    print(
                        f"Error: Failed to load JANAF table {filename} even after download"
                    )
                    return
            else:
                print(f"Error: Could not download JANAF table for {self.name}")
                return

        # define data
        self.T_grid = data[:, 0]
        self.G_grid = (
            1000 * (data[:, 2] - data[0, 2]) - data[:, 0] * data[:, 1]
        ) * Jmol_in_eV

    def _download_single_janaf_file(self, janaf_filename, dest_path):
        """Download a single JANAF file if it's in the supported list."""
        import urllib.request

        # Check if this file is in the supported list
        if janaf_filename not in SUPPORTED_JANAF_FILES:
            print(f"  {janaf_filename} is not in the list of supported JANAF files")
            return False

        # Ensure directory exists
        dest_dir = os.path.dirname(dest_path)
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)

        url = f"https://janaf.nist.gov/tables/{janaf_filename}"
        try:
            print(f"  Downloading {janaf_filename}...", end=" ")
            urllib.request.urlretrieve(url, dest_path)
            print("done")
            return True
        except Exception as e:
            print(f"failed (Error: {e})")
            return False

    def __eq__(self, other):
        return self.atoms == other.atoms and self.gas == other.gas

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return id(self)


# prepare all required species
H2gas = Species(
    ase.atoms.Atoms(
        "H2",
        [[0, 0, 0], [0, 0, 1.2]],
    ),
    gas=True,
    janaf_file="H-050.txt",
    name="H2gas",
)

H = Species(ase.atoms.Atoms("H"))

CH4gas = Species(
    ase.atoms.Atoms(
        "CH4",
        [
            [-2.14262, 3.03116, 0.00000],
            [-1.07262, 3.03116, 0.00000],
            [-2.49979, 4.03979, 0.00000],
            [-2.51306, 2.50700, 0.85611],
            [-2.49435, 2.53348, -0.87948],
        ],
    ),
    gas=True,
    janaf_file="C-067.txt",
    name="CH4gas",
)
CH4 = Species(
    ase.atoms.Atoms(
        "CH4",
        [
            [-2.14262, 3.03116, 0.00000],
            [-1.07262, 3.03116, 0.00000],
            [-2.49979, 4.03979, 0.00000],
            [-2.51306, 2.50700, 0.85611],
            [-2.49435, 2.53348, -0.87948],
        ],
    ),
    name="CH4",
)
O_atom = Species(
    ase.atoms.Atoms(
        "O",
        [[0, 0, 0]],
        cell=[10, 10, 10],
    ),
    name="O",
)
O2gas = Species(
    ase.atoms.Atoms(
        "O2",
        [[0, 0, 0], [0, 0, 1.2]],
        cell=[10, 10, 10],
    ),
    gas=True,
    janaf_file="O-029.txt",
    name="O2gas",
)

NOgas = Species(
    ase.atoms.Atoms(
        "NO",
        [[0, 0, 0], [0, 0, 1.2]],
        cell=[10, 10, 10],
    ),
    gas=True,
    janaf_file="N-005.txt",
    name="NOgas",
)

NO = Species(
    ase.atoms.Atoms(
        "NO",
        [[0, 0, 0], [0, 0, 1.2]],
        cell=[10, 10, 10],
    ),
    name="NO",
    janaf_file="N-005.txt",
)

NO2gas = Species(ase.atoms.Atoms(), gas=True, janaf_file="N-007.txt", name="NO2gas")

NO3gas = Species(ase.atoms.Atoms(), gas=True, janaf_file="N-009.txt", name="NO3gas")

COgas = Species(
    ase.atoms.Atoms(
        "CO",
        [[0, 0, 0], [0, 0, 1.2]],
        cell=[10, 10, 10],
    ),
    gas=True,
    janaf_file="C-093.txt",
    name="COgas",
)
CO = Species(
    ase.atoms.Atoms(
        "CO",
        [[0, 0, 0], [0, 0, 1.2]],
        cell=[10, 10, 10],
    ),
    name="CO",
)

CO2gas = Species(
    ase.atoms.Atoms(
        "CO2",
        [[0, 0, -1.2], [0, 0, 0], [0, 0, 1.2]],
        cell=[10, 10, 10],
    ),
    gas=True,
    janaf_file="C-095.txt",
    name="CO2gas",
)

NH3gas = Species(
    ase.atoms.Atoms(
        symbols="NH3",
        pbc=np.array([True, True, True], dtype=bool),
        cell=np.array([[10.0, 0.0, 0.0], [0.0, 10.0, 0.0], [0.0, 0.0, 10.0]]),
        positions=np.array(
            [
                [0.13288865, 0.13288865, 0.13288865],
                [-0.03325795, -0.03325795, 1.13361278],
                [-0.03325795, 1.13361278, -0.03325795],
                [1.13361278, -0.03325795, -0.03325795],
            ]
        ),
    ),
    gas=True,
    janaf_file="H-083.txt",
    name="NH3gas",
)

C2H4gas = Species(ase.atoms.Atoms(), gas=True, janaf_file="C-128.txt", name="C2H4gas")

HClgas = Species(ase.atoms.Atoms(), gas=True, janaf_file="Cl-026.txt", name="HClgas")

Cl2gas = Species(
    ase.atoms.Atoms(),
    gas=True,
    janaf_file="Cl-073.txt",
    name="Cl2gas",
)

H2Ogas = Species(
    ase.atoms.Atoms(),
    gas=True,
    janaf_file="H-064.txt",
    name="H2Ogas",
)

H2Oliquid = Species(
    ase.atoms.Atoms(),
    gas=False,
    janaf_file="H-063.txt",
    name="H2Oliquid",
)
