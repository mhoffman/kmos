.. image:: https://travis-ci.org/mhoffman/kmos.png?branch=master
    :target: https://travis-ci.org/mhoffman/kmos
.. image:: https://img.shields.io/badge/license-GPLv3-brightgreen.svg?style=flat-square)
    :target COPYING
.. image:: https://readthedocs.org/projects/kmos/badge/?version=latest
    :target: http://kmos.readthedocs.org/en/latest/?badge=latest
    :alt: Documentation Status
.. image:: https://badges.gitter.im/mhoffman/kmos.svg
   :alt: Join the chat at https://gitter.im/mhoffman/kmos
   :target: https://gitter.im/mhoffman/kmos?utm_source=badge&utm_medium=badge&utm_campaign=pr-badge&utm_content=badge

kmos: kMC modelling on steroids
=====================================
*a vigorous attempt to make lattice kinetic Monte Carlo modelling more accessible.*

Copyright (C) 2009-13 Max J. Hoffmann <mjhoffmann@gmail.com>

This program is free software; you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation; either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
this program; if not, see `http://www.gnu.org/licenses/ <http://www.gnu.org/licenses/>`_.

QUICKSTART
##########

Prepare a minimal input file with the following content and save it as ``mini_101.ini`` ::

    [Meta]
    author = Your Name
    email = you@server.com
    model_dimension = 2
    model_name = fcc_100

    [Species empty]
    color = #FFFFFF

    [Species CO]
    representation = Atoms("CO", [[0, 0, 0], [0, 0, 1.17]])
    color = #FF0000

    [Lattice]
    cell_size = 3.5 3.5 10.0

    [Layer simple_cubic]
    site hollow = (0.5, 0.5, 0.5)
    color = #FFFFFF

    [Parameter k_CO_ads]
    value = 100
    adjustable = True
    min = 1
    max = 1e13
    scale = log

    [Parameter k_CO_des]
    value = 100
    adjustable = True
    min = 1
    max = 1e13
    scale = log

    [Process CO_ads]
    rate_constant = k_CO_ads
    conditions = empty@hollow
    actions = CO@hollow
    tof_count = {'adsorption':1}

    [Process CO_des]
    rate_constant = k_CO_des
    conditions = CO@hollow
    actions = empty@hollow
    tof_count = {'desorption':1}

In the same directory run ``kmos export mini_101.ini``. You should now have a folder ``mini_101_local_smart``
in the same directory. ``cd`` into it and run ``kmos benchmark``. If everything went well you should see something
like ::

    Using the [local_smart] backend.
    1000000 steps took 1.51 seconds
    Or 6.62e+05 steps/s

In the same directory try running ``kmos view`` to watch the model run or fire up ``kmos shell``
to interact with the model interactively. Explore more commands with ``kmos help`` and please
refer to the documentation how to build complex model and evaluate them systematically. To test all bells and whistles try ``kmos edit mini_101.ini`` and inspect the model visually.

DOCUMENTATION
##############

Please refer to

* https://www.th4.ch.tum.de/index.php?id=1321
* http://mhoffman.github.io/kmos/
* http://kmos.readthedocs.org/
* https://github.com/jmlorenzi/intro2kmos

or links therein for tutorials, user guide, reference, and troubleshooting hints.

THANKS
######

This project draws on several other great Python modules, which are in turn
each free software and I would like to thank each of these projects for
making their code freely avalaible, namely:

* `Python <http://www.python.org>`_
* `ASE <https://wiki.fysik.dtu.dk/ase/>`_
* Numpy
* `f2py <http://cens.ioc.ee/projects/f2py2e/>`_
* `kiwi <http://www.async.com.br/projects/kiwi/>`_, gazpacho
* lxml and in particular `ElementTree <http://www.effbot.org/>`_

FILES
#####
| ├── COPYING                                      # Copy of GPLv3
| ├── INSTALL.rst                                  # installation instructions
| ├── README.rst                                   # This document
| ├── TODO.rst                                     # Ideas for improvement and new features
| ├── requirements.txt                             # Dependencies which can be installed via pip
| ├── setup.py                                     # setuptools using setup script
| ├── index.html                                   # landing website
| ├── kmos/                                        # the core kmos python modules
| │   ├── cli.py                                   # the command line interface
| │   ├── config.py                                # configuration of some project wide paths
| │   ├── fortran_src/                             # static Fortran 90 source files
| │   │   ├── assert.ppc                           # assertion macro
| │   │   ├── base.f90                             # the default kMC solver
| │   │   ├── base_lat_int.f90                     # slightly modified kMC solver for lat_int backend
| │   │   ├── kind_values.f90                      # definition of project wide kind values
| │   │   └── main.f90                             # source template for standalone Fortran 90 clients
| │   ├── gui/                                     # kmos.gui module
| │   │   ├── forms.py                             # view definitions (MVC) of editor GUI
| │   │   └── __init__.py                          # controller definitions (MVC) of editor GUI
| │   ├── __init__.py                              # root import module
| │   ├── io.py                                    # conversion between format: contains main Code Generator
| │   ├── kmc_editor.glade                         # Glade XML definiton for form interfaces
| │   ├── kmc_project_v0.1.dtd                     # Document Type Definition file of kMC project v0.1
| │   ├── kmc_project_v0.2.dtd                     # Document Type Definition file of kMC project v0.2
| │   ├── run.py                                   # High-level API for compiled models
| │   ├── species.py                               # Convenient interface for some reaction intermediates
| │   ├── types.py                                 # The basic classes for building kMC models
| │   ├── units.py                                 # Definition of conversion factor (CODATA 2010)
| │   ├── utils/                                   # Utility function that didn't fit elsewhere
| │   │   ├── __init__.py
| │   │   ├── ordered_dict.py
| │   │   ├── progressbar.py
| │   │   └── terminal.py
| │   └── view.py                                  # The runtime GUI for compiled models
| ├── doc/                                         # user guide, documentation, and reference
| │   └── source/                                  # documentation source file for compilation with Sphinx
| ├── examples/                                    # demoing non-standard features and useful idioms
| │   ├── AB_model.py                              # small demo file
| │   ├── benchmark_compilers_and_backends.sh      # demo file
| │   ├── crowded.xml                              # demo file
| │   ├── dreiD.xml                                # demo file for 3d model
| │   ├── dummy.xml                                # mininal model
| │   ├── model_Pt111_surface.py                   # demo file for non-rectangular lattice
| │   ├── multidentate.py                          # basic example for multidentate adsorption
| │   ├── render_bigcell.py                        # demo containing many sites
| │   ├── render_co_oxidation_ruo2.py              # demoing th CO Oxidation at RuO2(110) model
| │   ├── render_diffusion_model.py                # idioms for describing lateral interaction
| │   ├── render_einsD.py                          # simple 1-dimensional model
| │   ├── render_multispecies.py                   # render many species
| │   ├── render_pairwise_interaction.py           # idioms for describing lateral interaction
| │   ├── render_Pt_111.py                         # another non-rectangular lattice
| │   ├── render_sand_model.py                     # a neat diffusion model for non-trivial boundary conditions
| │   ├── run_in_multi_process.py                  # an example for parallelization over processes
| │   ├── run.py                                   # a high-level run script using the ModelRunner metaclass
| │   ├── ruptured_Pd.xml                          # a fcc(100) like surface with some sites missing
| │   └── small.xml                                # demo file
| ├── tests/                                       # Unit tests and test data
| └── tools                                        # Entry points for command line interface
|     ├── kmos
|     ├── kmos.bat
|     ├── kmos-build-standalone
|     └── kmos-install-dependencies-ubuntu
