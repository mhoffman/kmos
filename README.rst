kmos: kMC modelling on steroids - a vigorous attempt to make lattice kinetic
Monte Carlo modelling more accessible.

Copyright (C) 2009-11 Max J. Hoffmann <mjhoffmann@gmail.com>

This program is free software; you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation; either version 3 of the License, or (at your option) any later
version.

This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with
this program; if not, see `http://www.gnu.org/licenses/ <http://www.gnu.org/licenses/>`_.


DEPENDENCIES
############
In general this script has been developed and tested on Ubuntu 9.04-10.10 in
conjunction with both gfortran and ifort. So things will most likely work
best under a similar setup. Other than standard libraries you need to fetch:

*  python-numpy : contains f2py
*  python-lxml: project files are stored as XML
*  python-gtk: GUI toolkit
*  python-kiwi, gazpacho: frameworks for python-gtk



USAGE
#####
Start the main program with::
  kmos editor
and create your model. To test it you need to press 'Export source' choose a
folder where the source code will be dumped. Use a terminal to go to that
directory and run ./compile_for_f2py. If this finishes without complains
you can try running::
  kmos view

THANKS
######
This project draws on several other great Python modules, which are in turn
each free software and I would like to thank each of these project for
making their code avalaible for everyone, namely:

* `Python <http://www.python.org>`_
* `ASE <https://wiki.fysik.dtu.dk/ase/>`_
* Numpy
* `f2py <http://cens.ioc.ee/projects/f2py2e/>`_
* `kiwi <http://www.async.com.br/projects/kiwi/>`_, gazpacho
* lxml and in particular `ElementTree <http://www.effbot.org/>`_
* `pygtkcanvas <http://code.google.com/p/pygtkcanvas/>`_

