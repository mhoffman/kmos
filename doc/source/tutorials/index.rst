=========
Tutorials
=========

A first kMC Model--the GUI way
==============================

This tutorial will walk you through the creation of a
simple adsorption/desorption model on a simple cubic surface.
Despite its simplicity it touches all elements contained in
the GUI and could be considered from first-principles.

Meta
^^^^

Lattice
^^^^^^^

Species
^^^^^^^

Parameters
^^^^^^^^^^

Processes
^^^^^^^^^


Running the Model--the GUI way
==============================

A first kMC Model--the API way
==============================
Since the GUI used in the first subsection is nothing
but a frontend to the various datatypes, you can just as
well write models by instantiating and adding different
parts of the model directly in python. This way might look
rather arcane for simple models in the beginning, however
it starts to really pay off as soon as you want to 
make a copy of a model which is almost identical with the
only difference that ...


From scratch
^^^^^^^^^^^^

We start by making the necessary import statements::
  from kmos.types import *
  from kmos.io import *

which import all classes that make up a kMC project. The functions
from `kmos.io` will only be needed at the end to save the project
or to export compilable code.


Now you have to instantiate a new project and fill in meta information::
  pt = ProjectTree()




Running the Model--the API way
==============================

A More Complicated Structure
==============================

More Dimensions
===============

Chess Project
=============
