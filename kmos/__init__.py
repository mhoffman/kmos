"""
Feature overview
================
With kmos you can:

    * easily create and modify kMC models through GUI
    * store and exchange kMC models through XML
    * generate fast, platform independent, self-contained code [#code]_
    * run kMC models through GUI or python bindings

kmos has been developed in the context of first-principles based modelling
of surface chemical reactions but might be of help for other types of
kMC models as well.

kmos' goal is to significantly reduce the time you need
to implement and run a lattice kmc simulation. However it can not help
you plan the model.


kmos can be invoked directly from the command line in one of the following
ways::

    kmos [help] (all|benchmark|build|edit|export|export-settings|help|import|rebuild|run|view) [options]

or it may be used as an API via the kmos module.

.. rubric:: Footnotes

.. [#code] The source code is generated in Fortran90, written in a modular
            fashion. Python bindings are generated using `f2py  <http://cens.ioc.ee/projects/f2py2e/>`_.
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


#import kmos.types
#import kmos.io

__version__ = "0.3.16"
VERSION = __version__

from kmos.utils import evaluate_rate_expression
