Getting Started
===============

Introduction
^^^^^^^^^^^^

.. automodule:: kmos




Installation
^^^^^^^^^^^^

You can fetch the current version of kmos using *git* ::

    git clone http://www.github.com/mhoffman/kmos


and install it using *setuptools* ::

    ./setup.py install [--user]


In order to use all features of kmos you have to install
a number of dependencies. This should not be very difficult
on a recent Linux distribution with package management. So
on Ubuntu it suffices to call::

  sudo apt-get install gazpacho gfortran python-dev \
                       python-glade2 python-kiwi python-lxml \
                       python-matplotlib python-numpy \
                       python-pygoocanvas python-scipy


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
needed in the environment where the model development happens.
The generated code needed to run a model actually has no
dependencies at all.

To ease the installation further on Ubuntu one can also simply run::

 kmos-install-dependencies-ubuntu 


.. todo ::

    add pip way or something alike to automatically
    install dependencies.


.. todo ::

   test installation on other platmforms

kMC Modelling
^^^^^^^^^^^^^

A good way to define a model is to use a paper and pencil to draw
your lattice, choose the species that you will need, draw
each process and write down an expression for each rate constant, and
finally fix all energy barriers and external parameters that you will need.
Putting a model prepared like this into a computer is a simple exercise.
You enter a new model by filling in

    * meta information
    * lattice
    * species
    * parameters
    * processes

in roughly this order or open an existing one by opening a kMC XML file.

If you want to see the model run
`kmos export <xml-file>` and you will get a subfolder with a self-contained
Fortran90 code, which solves the model. If all necessary dependencies are
installed you can simply run `kmos view` in the export folder.

