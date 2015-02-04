Installation on Ubuntu Linux
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can fetch the current version of kmos using *git* ::

    git clone http://www.github.com/mhoffman/kmos


and install it using *setuptools* ::

    ./setup.py install [--user]


or if you have `pip <http://www.pip-installer.org/en/latest/installing.html>`_ run ::

    pip install python-kmos --upgrade [--user]

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

Unfortunately Debian/Ubuntu have discontinued maintaining the gazpacho package which I find very unfortunate since it eased gtk GUI building a lot and I haven't found a simple transition path (simple as in one reliable conversion script and two changed import lines) towards gtkbuilder. Therefore for the moment I can only suggest to fetch the latest old package from e.g. `Debian Packages <https://packages.debian.org/de/squeeze/all/gazpacho/download>`_ and install it manually with ::

    sudo dpkg -i gazpacho_*.deb



If you think this dependency list hurts. Yes, it does!
And I am happy about any suggestions how to
minimize it. However one should note these dependencies are only
required for the model development. Running a model has virtually
no dependencies except for a Fortran compiler.

To ease the installation further on Ubuntu one can simply run::

 kmos-install-dependencies-ubuntu


Installation on openSUSE 12.1 Linux
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

On a recent openSUSE some dependencies are distributed a little
different but nevertheless doable. We start by install some
package from the repositories ::

  sudo zypper install libgfortran46, python-lxml, python-matplotlib, \
                      python-numpy, python-numpy-devel, python-goocanvas,
                      python-imaging

And two more packages SUSE packages have to be fetched from the
openSUSE `build service <https://build.opensuse.org/>`_

- `gazpacho <https://build.opensuse.org/package/files?package=gazpacho&project=home%3Ajoshkress>`_
- `python-kiwi <https://build.opensuse.org/package/files?package=python-kiwi&project=home%3Ajoshkress>`_


For each one just download the \*.tar.bz2 files. Unpack them and inside
run ::

  python setup.py install

In the same vein you can install ASE. Download a recent version
from the `DTU website <https://wiki.fysik.dtu.dk/ase/download.html>`_
unzip it and install it with ::

  python setup.py install



Installation on openSUSE 13.1 Linux
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

In order to use the editor GUI you will want to install python-kiwi (not KIWI)
and right now you can find a recent build `here <https://build.opensuse.org/package/show/home:leopinheiro/python-kiwi>`_ .

Installation on Mac OS X 10.10 or above
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

There is more than one way to get required dependencies. I have tested MacPorts and worked quite well.

#. Get MacPorts
    Search for MacPorts online, you'll need to install Xcode in the process

#. Install Python, lxml, numpy, ipython, ASE, gcc48. I assume you are using Python 2.7.
   kmos has not been thoroughly tested with Python 3.X, yet, but should not be too hard.
    Having MacPorts this can be as simple as ::

        sudo ports install -v py27-ipython
        sudo port select --set ipython ipython ipython27

        sudo port install gcc48
        sudo port select --set gcc mp-gcc48 # need to that f2py finds a compiler

        sudo port install py27-readline
        sudo port install py27-goocanvas
        sudo port install py27-lxml
        sudo port install kiwi
        # possibly more ...

        # if you install these package manually, skip pip :-)
        sudo port install py27-pip
        sudo port select --set pip pip27

        pip install python-ase --user
        pip install python-kmos --user


Installation on windoze 7
^^^^^^^^^^^^^^^^^^^^^^^^^
In order for kmos to work in a recent windoze we need a
number of programs.

#. **Python**
   If you have no python previously installed you should try
   `Enthought Python Distribution`_ (EPD) in its free version since it
   already comes with a number of useful libraries such a numpy, scipy,
   ipython and matplotlib.

   Otherwise you can simply download Python from `python.org`_ and
   this installation has been successfully tested using python 2.7.


#. **numpy**
   Fetch it for `your version` of python from
   `sourceforge's Numpy site <http://sourceforge.net/project/numpy>`_
   and install it. [Not needed with EPD ]

#.  **MinGW**
    provides free Fortran and C compilers and can be obtained from the
    `sourceforge's MinGW site <http://sourceforge.net/projects/mingw/>`_ .
    Make sure you make a tick for the Fortran and the C compiler.

#. **pyGTK**
   is needed for the GUI frontend so fetch the
   `all-in-one <http://www.pygtk.org/downloads.html>`_ bundle installer and
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
`NIST website <http://kinetics.nist.gov/janaf/>`_
in the tab-delimited text format
to the `janaf_data` directory. To download the ASCII file,
search for your molecule. In the results page click on 'view'
under 'JANAF Table' and click on 'Download table in tab-delimited text format.'
at the bottom of that page.



.. _Enthought Python Distribution: http://www.enthought.com/products/epd_free.php
.. _python.org: http://www.python.org/download
.. _lxml 2.2.8: http://pypi.python.org/pypi/lxml/2.2.8
.. todo :: test installation on other platforms
