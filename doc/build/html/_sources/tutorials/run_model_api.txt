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

  model = KMC_Model()

As you can see by default the model prints a disclaimer
and all rate constants, which can each be turned off
by instantiating ::

  model = KMC_Model(print_rates=False, banner=False)

Let's say you want to change the temperature and a partial pressure of
the model you could type ::

  model.parameters.T = 550
  model.parameters.p_COgas = 0.5

and all rate constants will be instantly updated. In order get a quick
overview of the current settings you can issue e.g. ::

  print(model.parameters)
  print(model.rate_constants

or just ::

  print(model)

Now an instantiated und configured model has mainly two functions: run
kMC steps and report its current configuration.

In order to propagate the model `n` steps you can say ::

  model.do_steps(n)

and to analyze the current state you can use ::

  
  model.get_atoms()

This will return an ASE atoms object of the current system, but
it also contains some additional data piggy-backed such as ::

  model.get_occupation_header()
  atoms.occupation

  model.get_tof_header()
  atoms.tof_data


  atoms.kmc_time
  atoms.kmc_step

These quantities are often sufficient when running and simulating
a catalyst surface, but of course the model could be expanded
to more observables.

Lastly it is important to call ::

  model.deallocate()

once the simulation if finished as this frees the memory
allocated by the Fortan modules. This is particularly
necessary if you want to run more than one simulation
in one script.
