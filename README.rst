kmos: kMC modelling on steroids - a vigorous attempt to make lattice kinetic
Monte Carlo modelling more accessible.

Copyright (C) 2009-12 Max J. Hoffmann <mjhoffmann@gmail.com>

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
*  python-gtk2: GUI toolkit
*  python-kiwi, gazpacho: frameworks for python-gtk



USAGE
#####
somehow

Start the main program with ::

  kmos editor

and create your model or create using IPython and the tutorials in
the documentation. Both ways will give a XML file in the end that
contains the entire definition of your kMC model. Run ::

  kmos export <xml-file>

and you will find a new folder under the same name with the compiled
model and self-contained source code. Inside that directory run ::

  kmos view

and readily watch your model and manipulate parameters at the same time.

THANKS
######

This project draws on several other great Python modules, which are in turn
each free software and I would like to thank each of these projects for
making their code avalaible, namely:

* `Python <http://www.python.org>`_
* `ASE <https://wiki.fysik.dtu.dk/ase/>`_
* Numpy
* `f2py <http://cens.ioc.ee/projects/f2py2e/>`_
* `kiwi <http://www.async.com.br/projects/kiwi/>`_, gazpacho
* lxml and in particular `ElementTree <http://www.effbot.org/>`_
* `pygtkcanvas <http://code.google.com/p/pygtkcanvas/>`_
