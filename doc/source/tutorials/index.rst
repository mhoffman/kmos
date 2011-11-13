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

The example sketched out here leads you to a kMC model for CO adsorption
and desorption on Pd(100) including a simple lateral interaction. Granted
this hardly excites surface scientists but we need to start somewhere, right?


Now you have to instantiate a new project and fill in meta information::

  pt = Project()
  pt.meta.author_name = 'Your Name'
  pt.meta.author_email = 'your.name@server.com'
  pt.meta.model_name = 'MyFirstModel'
  pt.meta.model_dimension = 2


Next you could add some species or states. For surface science simulations
it is useful to define an *empty* state, so we add::

 pt.add_species(Species(name='empty'))

and some surface species. Given you want to simulate CO adsorption and
desorption on a single crystal surface we say::
  
  pt.add_species(Species(name='CO',
                         representation='Atoms("CO",[[0,0,0],[0,0,1.2]]))

where the string passed as `representation` is a string representing
a CO molecule which can be evaluated in 






Running the Model--the API way
==============================

A More Complicated Structure
==============================

More Dimensions
===============

Chess Project
=============
