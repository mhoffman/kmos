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
required for the model development. Running a model has virtually
no dependencies except for a Fortran compiler.

To ease the installation further on Ubuntu one can simply run::

 kmos-install-dependencies-ubuntu 


.. todo ::

    add pip way or something alike to automatically
    install dependencies.


.. todo ::

   test installation on other platforms
