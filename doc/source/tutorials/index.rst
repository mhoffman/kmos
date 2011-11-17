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

We start by making the necessary import statements (in *python* or better *ipython*)::

  from kmos.types import *
  from kmos.io import *
  import numpy as np

which import all classes that make up a kMC project. The functions
from `kmos.io` will only be needed at the end to save the project
or to export compilable code.

The example sketched out here leads you to a kMC model for CO adsorption
and desorption on Pd(100) including a simple lateral interaction. Granted
this hardly excites surface scientists but we need to start somewhere, right?


Now you have to instantiate a new project and fill in meta information::

  pt = Project()
  pt.meta.author = 'Your Name'
  pt.meta.email = 'your.name@server.com'
  pt.meta.model_name = 'MyFirstModel'
  pt.meta.model_dimension = 2


Next you could add some species or states. For surface science simulations
it is useful to define an *empty* state, so we add::

 pt.add_species(Species(name='empty'))

and some surface species. Given you want to simulate CO adsorption and
desorption on a single crystal surface we say::
  
  pt.add_species(Species(name='CO',
                         representation="Atoms('CO',[[0,0,0],[0,0,1.2]])"))

where the string passed as `representation` is a string representing
a CO molecule which can be evaluated in 


Once you have all species declared is a good time to think about the geometry.
To keep it simple we will stick with a simple-cubic lattice in 2D which
could for example represent the (100) surface of a fcc crystal with only
one adsorption site per unit cell. So we start by giving our layer a name::

  layer = Layer(name='simple_cubic')

and adding a site::
  
  layer.sites.append(Site(name='hollow', pos='0.5 0.5 0.5',
                          default_species='empty'))


Where `pos` is given in fractional coordinates, so this site
will be in the center of the unit cell. Finally we have to
add the newly created layer to our project::

  pt.add_layer(layer)


Simple, huh? Now you wonder where all the rest of the geometry went?
The reason is simple: the geometric location of a site is actually
meaningless for the primary task a kMC simulation is solving. In
order to solve the master equation none of the numerical coordinates
of any lattice, site matters since the master equation is only
defined in terms of states and transition between these state. However
to allow a graphical representation of the simulation one can add geometry
as you have already done for the site. The size of the unit cell can
be set via::

  pt.lattice.cell = np.diag([3.5, 3.5, 10])

which are proto-typical dimension for single-crystal surface in
angstrom.



Ok, let us see we managed so far: you have a lattice with a
site that can be either empty for occupied with CO.

The remaining work is to populate the process list and the
parameter list. The parameter list defines the parameters
that can be used in the expressions for the rate constants of
each process. In principle one could to without the parameter
list and simply hard code all parameters in the process list,
however one looses some nifty functionality like easily
changing parameters on-the-fly or even interactively.
A second benefit is that you can clearly separate the kinetic
model from the barrier input which usually has a different
origin such as a DFT calculation.


In practice filling the parameter list and the process
list is often an interactive process, however since
we have a fairly short list, we can try to set all parameters
at once.

First of all you went to define the external parameters to
which our model is coupled. Here we use the temperature
and the CO partial pressure::

  pt.add_parameter(Parameter(name='T', value=600., adjustable=True, min=400, max=800))
  pt.add_parameter(Parameter(name='p_CO', value=1., adjustable=True, min=1e-10, max=1.e2))


Here the value given should be consideredd a default value and if
one sets adjustable to True, the viewer front-end will feature
little scroll bars allowing to adjust them interactively.

To describe the adsorption rate constant you will need the area
of the unit cell::

  pt.add_parameter(Parameter(name='A',value='(3.5*angstrom)**2'))

Last but not least one needs a binding energy of the particle on
the surface. Since without further ado we have no value for the
gas phase chemical potential, we'll just call it deltaG and keep
it adjustable::

  pt.add_parameter(Parameter(name='deltaG', value='-0.5', adjustable=True,
                             min=-1.3, max=0.3))

Last but not least we need to have at least two processes. A process in kMC
means that a certain local configuration must be given so that something
can happen at a certain rate constant. In the framework here this is
phrased in terms of 'conditions' and 'actions'. So for example an
adsorption requires at least one site to be empty (condition). Then this
site can be occupied by CO (action) with a certain rate constant. Written
down in code this looks as follows. First we need a coord::
  
  coord = pt.lattice.generate_coord('hollow.(0,0,0).simple_cubic')

which we can now use::

  pt.add_process(Process(name='CO_adsorption',
                 condition_list=[Condition(coord=coord, species='empty')],
                 action_list=[Action(coord=coord, species='CO')],
                 rate_constant='p_CO*bar*A/sqrt(2*pi*umass*m_CO/beta)'))

Now you might wonder, how come we can simply use m_CO and beta and such.
Well, that is because we evaluator will to some trickery to resolve such
terms. So beta will be first be translated into 1/(kboltzmann*T) and as
long as you have set a parameter `T` before, this will go through. Same
is true for m_CO, here the atomic masses are looked up and added. Note
that we need conversion factors of bar and umass.

Then the desorption process is almost the same, except the reverse::

  pt.add_process(Process(name='CO_desorption',
                 condition_list=[Condition(coord=coord, species='CO')],
                 action_list=[Action(coord=coord, species='empty')],
                 rate_constant='p_CO*bar*A/sqrt(2*pi*umass*m_CO/beta)*exp(-deltaG*eV)'))


And that is it! First it is a good idea to save your work::

  pt.export_xml_file('myfirst_kmc.xml')

and next you can export the source code::

  kmos.io.export_source(pt)

Now is the time to leave the python shell. In the current
directory you should see a MyFirstModel.xml and a folder
named MyFirstModel. The latter contains all source code.


If you now `cd` to that folder and run::

  kmos build

right there, you should get a binary named `kmc_model.so`.
Now run::

  kmos view

... and dada! Your first running kMC model right there!


If you wonder why the CO molecule are basically just dangling
there in mid-air that because you have now layer setup, yet.
Choose a transition metal of your choice and add it to the
lattice setup for extra credit :-).

Running the Model--the API way
==============================

A More Complicated Structure
==============================

More Dimensions
===============

Chess Project
=============
