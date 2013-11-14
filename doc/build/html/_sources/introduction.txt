Introduction
============

.. automodule:: kmos




Installation
============

You can fetch the current version of kmos using *git* ::

    git clone http://www.github.com/mhoffman/kmos


and install it using *setuptools* ::

    ./setup.py install [--user]


.. todo ::

    add description of dependencies

.. todo ::

    add pip way or something alike to automatically
    install dependencies.

kMC Modelling
=============

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

