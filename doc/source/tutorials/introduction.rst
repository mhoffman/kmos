Getting Started
===============

Introduction
^^^^^^^^^^^^

.. automodule:: kmos




Installation on Ubuntu Linux
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can fetch the current version of kmos using *git* ::

    git clone http://www.github.com/mhoffman/kmos


and install it using *setuptools* ::

    ./setup.py install [--user]


To use the core functionality
(programmatic model setup, code generation, model execution)
kmos has a fairly modest depedency foot-print. You will need ::

  python-numpy, a Fortran compiler, python-lxml

In order to watch the model run on screen you will additionally
need ::

  python-matplotlib, python-ase

Finally in order to use all features, in particular the GUI
model editor of kmos you have to install
a number of dependencies. This should not be very difficult
on a recent Linux distribution with package management. So
on Ubuntu it suffices to call::

  sudo apt-get install gazpacho gfortran python-dev \
                       python-glade2 python-kiwi python-lxml \
                       python-matplotlib python-numpy \
                       python-pygoocanvas


and if you haven't already installed it, one way to fetch the
atomic simulation environment (ASE) is currently to ::

  sudo add-apt-repository ppa:campos-dev/campos
  sudo apt-get update
  sudo apt-get install python-ase

Or go to their `website <https://wiki.fysik.dtu.dk/ase/download.html>`_
to fetch the latest version.

If you think this dependency list hurts. Yes, it does!
And I am happy about any suggestions how to
minimize it. However one should note these dependencies are only
required for the model development. Running a model has virtually
no dependencies except for a Fortran compiler.

To ease the installation further on Ubuntu one can simply run::

 kmos-install-dependencies-ubuntu


.. todo ::

    add pip way or something alike to automatically
    install dependencies.


Installation in openSUSE 12.1 Linux
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

On recent openSUSE some dependencies are distributed a little
different but nevertheless doable. We start by install some
package from the repositories ::

  sudo zypper install libgfortran46, python-lxml, python-matplotlib, \


Installation on windoze 7
^^^^^^^^^^^^^^^^^^^^^^^^^
In order for kmos to work in a recent windoze we need a
number of programs.

#. **Python**
   If you have no python previously installed you might consider the
   `Enthought Python Distribution`_ in its free version because it
   already packages a number of useful libraries such a numpy, scipy,
   ipython and matplotlib.

   Otherwise you can simply download Python from `python.org`_ and
   this installation has been successfully tested using python 2.7.


#. **numpy**
   Fetch it for `your version` of python from
   `sourceforge's Numpy site <http://sourceforge.net/project/numpy>`_
   and install it.

#.  **MinGW**
    provides free Fortran and C compilers and can be obtained from the
    `sourceforge's MinGW site <http://sourceforge.net/projects/mingw/>`_ .
    Make sure you make a tick for the Fortran and the C compiler.

#. **GTK**
   is needed for the GUI frontend so fetch the
   `all-in-one <http://www.gtk.org/download/>`_ installer and
   install most of it.

#. **lxml**
   is an awesome library to process xml files, which has unfortunately
   not fully found its way into the standard library. As of this writing
   the latest version with prebuilt binaries is `lxml 2.2.8`_ and installation
   works without troubles.

#. **ASE**
   is needed for the representation of atoms in the frontend. So
   download the latest from the
   `DTU website <https://wiki.fysik.dtu.dk/ase/>`_
   and install it. This has to be installed using e.g. the powershell.
   So after unpacking it, fire up the powershell, cd to the directory
   and run ::

    python setup.py install

   in there. Note that there is currently a slight glitch in the
   `setup.py` script on windoze, so open `setup.py` in a text
   editor and find the line saying ::

     version = ...

   comment out the lines above it and hard-code the current version
   number.

#. **kmos**
   is finally what we are after, so download the latest version
   from `github <http://mhoffman.github.com/kmos/>`_ and install
   it in the same way as you installed **ASE**.


There are probably a number of small changes you have to make
which are not described in this document. Please post questions
and comments in the
`issues forum <https://github.com/mhoffman/kmos/issues>`_ .





.. _Enthought Python Distribution: http://www.enthought.com/products/epd_free.php
.. _python.org: http://www.python.org/download
.. _lxml 2.2.8: http://pypi.python.org/pypi/lxml/2.2.8
.. todo :: test installation on other platforms
