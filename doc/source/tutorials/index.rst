=========
Tutorials
=========

.. include:: introduction.rst



.. include:: first_model_api.rst

A first kMC Model--the GUI way
==============================

This tutorial will walk you through the creation of a
simple adsorption/desorption model on a simple cubic surface.
Despite its simplicity it touches all elements contained in
the GUI and could be considered from first-principles.

Running the Model--the GUI way
==============================

After successfully exporting and compiling a model you get
two files: kmc_model.so and kmc_settings.py. These two files
are technically all you need for simulations. So a simple
way to view the model is the ::

  kmos view

command from the command line. For this two work you need to
be in the same directory as these two file (more precisely
these two files need to be in the python import path) and
you should see an instance of your model running. This feature
can be quite useful to quickly obtain an intuitive understanding
of the model at hand. A lot of settings can be changed through
the kmc_settings.py such as rate constant or parameters. To
be even more interactive you set a parameter to be adjustable.
This can happen either in the generating XML file or directly
in the kmc_settings.py. Also make sure to set sensible minimum
and maximum values.

.. TODO:: add recording function

Running the Model--the API way
==============================

In order to analyze a model in a more quantitative way it is
more practical to write small client scripts that directly
talk to the runtime API. As time passes and more of these
scripts are written over and over some standard functionality
will likely be integrated into the runtime API. For starters
a simple script could look as follows ::

  #!/usr/bin/env python

  from kmos.run import KMC_Model

  
.. TODO: Finish

A More Complicated Structure
==============================

More Dimensions
===============

Chess Project
=============
