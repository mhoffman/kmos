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

The most important method is of course how to run
the model, which you can do by saying ::

  model.do_steps(100000)

which would run the model by 100,000 kMC steps.

Let's say you want to change the temperature and a partial pressure of
the model you could type ::

  model.parameters.T = 550
  model.parameters.p_COgas = 0.5

and all rate constants are instantly updated. In order get a quick
overview of the current settings you can issue e.g. ::

  print(model.parameters)
  print(model.rate_constants)

or just ::

  print(model)

Now an instantiated und configured model has mainly two functions: run
kMC steps and report its current configuration.

To analyze the current state you may use ::

  atoms = model.get_atoms()

.. note::

  If you want to fetch data from the current state without
  actually visualizing the geometry can speed up the get_atoms()
  call using ::

    atoms = model.get_atoms(geometry=False)

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
to more observables. The Fortran modules `base`, `lattice`,
and `proclist` are atttributes of the model instance so,
please feel free to explore the model instance e.g. using
ipython and ::

  model.base.<TAB>
  model.lattice.<TAB>
  model.proclist.<TAB>

etc..

The `occupation` is a 2-dimensional array which contains
the `occupation` for each surface `site` divided by
the number of unit cell. The first slot
denotes the species and the second slot denotes the
surface site, i.e. ::

  occupation[species, site-1]

So given there is a `hydrogen` species
in the model, the occupation of `hydrogen` across all site
type can be accessed like ::

  hydrogen_occupation = occupation[model.proclist.hydrogen]

To access the coverage of one surface site, we have to
remember to subtract 1, when using the the builtin constants,
like so ::

  hollow_occupation = occupation[:, model.lattice.hollow-1]

Lastly it is important to call ::

  model.deallocate()

once the simulation if finished as this frees the memory
allocated by the Fortan modules. This is particularly
necessary if you want to run more than one simulation
in one script.


.. _manipulate_model_runtime:

Manipulating the Model at Runtime
=================================

It is quite easy to change not only model parameters but
also the configuration at runtime. For instance if one
would like to prepare a surface with a certain configuration
or pattern.

Given you instantiated a `model` instance a site occupation
can be changed by calling ::

  model.put(site=[x,y,z,n], model.proclist.<species>)

However if changing many sites at once this is quite inefficient,
since each `put` call, adjusts the book-keeping database. To circumvent
this you can use the `_put` method, like so ::

  model._put(...)
  model._put(...)
  ...
  model._adjust_database()

though at the end one must not forget to call `_adjust_database()`
before executing any next step or the database of available processes
is inaccurate and the model instance will crash soon.

Running models in parallel
==========================

Due to the global clock in kMC there seems to be no
simple and efficient way to parallelize a kMC program.
kmos certainly cannot parallelize a single system over
processors. However one can run several kmos instances
in parallel which might accelerate sampling or efficiently
check for steady state conditions.

However in many applications it is still useful to
run several models seperately at once, for example to scan
some set of parameters one a multicore computer. This
kind of problem can be considered `embarrasingly parallel`
since the require no communication between the runs.

This is made very simple through the `multiprocessing`,
which is in the Python standard library since version 2.6.
For older versions this needs to be `downloaded <http://pypi.python.org/pypi/multiprocessing/>`
and installed manually. The latter is very
straightforward.


Then besides `kmos` we need to import `multiprocessing` ::

  from multiprocessing import Process
  from numpy import linspace
  from kmos.run import KMC_Model

and let's say you wanted to scan a range of temperature,
while keeping all other parameteres constant. You first
define a function, that takes a set of temperatures
and runs the simulation for each ::


  def run_temperatures(temperatures):
      for T in temperatures:
          model = KMC_Model()
          model.parameters.T = T
          model.do_steps(100000)

          # do some evaluation

          model.deallocate()


In order to split our full range of input parameters, we
can use a utility function ::

  from kmos.utils import split_sequence


All that is left to do, is to define the input parameters,
split the list and start subprocesses for each sublist ::

  if __name__ == '__main__':
      temperatures = linspace(300, 600, 50)
      nproc = 8
      for temperatures in split_sequence(temperatures, nproc):
          p = Process(target=run_temperatures, args=(temperatures, ))
          p.start()
