Running the Model--the GUI way
==============================

After successfully exporting and compiling a model you get
two files: kmc_model.so and kmc_settings.py. These two files
are really all you need for simulations. So a simple
way to view the model is the ::

  kmos view

command from the command line. For this two work you need to
be in the same directory as these two file (more precisely
these two files need to be in the python import path) and
you should see an instance of your model running.
This feature can be quite useful to quickly obtain an
intuitive understanding of the model at hand. A lot of settings
can be changed through the kmc_settings.py such as rate constant
or parameters.
To be even more interactive you can set a parameter
to be adjustable.  This can happen either in the generating XML
file or directly in the kmc_settings.py. Also make sure to set
sensible minimum and maximum values.


How To Prepare a Model and Run It Interactively
===============================================

If you want to prepare a model in a certain
way (parameters, size, configuration) and
then run it interactively from there, there
is in easy way, too.  Just write a little python
script. The with-statement is nice because it takes
care of the correct allocation and deallocation ::

  #!/usr/bin/env python

  from kmos.run import KMC_Model
  from kmos.view import main


  with KMC_Model(print_rates=False, banner=False) as model:
    model.settings.simulation_size = 5

  with KMC_Model(print_rates=False, banner=False) as model:
      model.do_steps(int(1e7))
      model.double()
      model.double()
      # one or more changes to the model
      # ...
      main(model)

Or you can use the hook in the `kmc_settings.py` called `setup_model`.
This function will be invoked at startup every time you call ::

  kmos view, run, or benchmark

Though it can easily get overwritten, when exporting or rebuilding.
To minimize this risk, you e.g. place the `setup_model` function
in a separate file called `setup_model.py` and insert into kmc_settings.py ::

  from setup_model import setup_model

Next time you overwrite `kmc_settings.py` you just need to add this line
again.
