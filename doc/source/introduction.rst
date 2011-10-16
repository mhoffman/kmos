Introduction
============

kmos is a vigorous attempt to make (lattice) kMC modelling more accessible.

Feature overview
================
With kmos you can:

    * easily create and modify kMC models through GUI
    * store and exchange kMC models through XML
    * generate fast, platform independent, self-contained code
    * run kMC models through GUI or python bindings

kmos has been developed in the context of first-principles based modelling
of surface chemical reactions but might be of help for other kMC models
as well.

kmos' goal is to significantly reduce the time you need
to implement and run a lattice kmc simulation. However it can not help
you plan the model. 


kmos can be invoked directly from the command line in one of the following 
ways::

    kmos [help] (edit|export|view) [options]



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

