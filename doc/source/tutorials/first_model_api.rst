.. _api-tutorial:

A first kMC Model--the API way
==============================

In general there are two interfaces to *defining* a new
model: A GUI and an API. While the GUI can be quite
nice especially for beginners, it turns out that the
API is better maintained simply because ... well, maintaing
a GUI is a lot more work.

So we will start by learning how to setup the model using the
API which will turn out not to be hard at all. It is knowing howto
do this will also pay-off especially if you starting tinkering
with your existing models and make little changes here and there.



Construct the model
^^^^^^^^^^^^^^^^^^^

We start by making the necessary import statements (in `*python* <http://python.org>`_ or better `*ipython* <http://ipython.org>`_)::

  from kmos.types import *
  from kmos.io import *
  import numpy as np

which imports all classes that make up a kMC project. The functions
from `kmos.io` will only be needed at the end to save the project
or to export compilable code.

The example sketched out here leads you to a kMC model for CO adsorption
and desorption on Pd(100) including a simple lateral interaction. Granted
this hardly excites surface scientists but we need to start somewhere, right?


First you should instantiate a new project and fill in meta information ::

  pt = Project()
  pt.set_meta(author = 'Your Name',
              email = 'your.name@server.com',
              model_name = 'MyFirstModel',
              model_dimension = 2,)


Next you add some species or states. Note that whichever
species you add first is the default species with which all sites in the
system will be initialized. Of course this can be changed later

For surface science simulations it is useful to define an
*empty* state, so we add ::

 pt.add_species(name='empty')

and some surface species. Given you want to simulate CO adsorption and
desorption on a single crystal surface you would say ::

  pt.add_species(name='CO',
                 representation="Atoms('CO',[[0,0,0],[0,0,1.2]])")

where the string passed as `representation` is a string representing
a CO molecule which can be evaluated in `ASE namespace <https://wiki.fysik.dtu.dk/ase/ase/atoms.html>`_.

Once you have all species declared is a good time to think about the geometry.
To keep it simple we will stick with a simple-cubic lattice in 2D which
could for example represent the (100) surface of a fcc crystal with only
one adsorption site per unit cell. You start by giving your layer a name ::

  layer = pt.add_layer(name='simple_cubic')

and adding a site ::

  layer.sites.append(Site(name='hollow', pos='0.5 0.5 0.5',
                          default_species='empty'))


Where `pos` is given in fractional coordinates, so this site
will be in the center of the unit cell.

Simple, huh? Now you wonder where all the rest of the geometry went?
For a simple reason: the geometric location of a site is
meaningless from a kMC point of view. In order to solve the master
equation none of the numerical coordinates
of any lattice sites matter since the master equation is only
defined in terms of states and transition between these. However
to allow a graphical representation of the simulation one can add geometry
as you have already done for the site. You set the size of the unit cell
via ::

  pt.lattice.cell = np.diag([3.5, 3.5, 10])

which are prototypical dimensions for a single-crystal surface in
Angstrom.

Ok, let us see what we managed so far: you have a *lattice* with a
*site* that can be either *empty* or occupied with *CO*.


Populate process list and parameter list
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The remaining work is to populate the `process list` and the
`parameter list`. The parameter list defines the parameters
that can be used in the expressions of the rate constants.
In principle one could do without the parameter
list and simply hard code all parameters in the process list,
however one looses some nifty functionality like easily
changing parameters on-the-fly or even interactively.

A second benefit is that you achieve a clear separation
of the kinetic model from the barrier input,
which usually has a different origin.

In practice filling the parameter list and the process
list is often an iterative process, however since
we have a fairly short list, we can try to set all parameters
at once.

First of all you want to define the external parameters to
which our model is coupled. Here we use the temperature
and the CO partial pressure::

  pt.add_parameter(name='T', value=600., adjustable=True, min=400, max=800)
  pt.add_parameter(name='p_CO', value=1., adjustable=True, min=1e-10, max=1.e2)

You can also set a default value and a minimum and maximum value
set defines how the scrollbars a behave later in the runtime GUI.

To describe the adsorption rate constant you will need the area
of the unit cell::

  pt.add_parameter(name='A', value='(3.5*angstrom)**2')

Last but not least you need a binding energy of the particle on
the surface. Since without further ado we have no value for the
gas phase chemical potential, we'll just call it deltaG and keep
it adjustable ::

  pt.add_parameter(name='deltaG', value='-0.5', adjustable=True,
                             min=-1.3, max=0.3)

To define processes we first need a coordinate [#coord_minilanguage]_  ::

  coord = pt.lattice.generate_coord('hollow.(0,0,0).simple_cubic')


Then you need to have at least two processes. A process or elementary step in kMC
means that a certain local configuration must be given so that something
can happen at a certain rate constant. In the framework here this is
phrased in terms of 'conditions' and 'actions'. [#proc_minilanguage]_
So for example an adsorption requires at least one site to be empty
(condition). Then this site can be occupied by CO (action) with a
rate constant. Written down in code this looks as follows ::

  pt.add_process(name='CO_adsorption',
                 conditions=[Condition(coord=coord, species='empty')],
                 actions=[Action(coord=coord, species='CO')],
                 rate_constant='p_CO*bar*A/sqrt(2*pi*umass*m_CO/beta)')



.. note:: In order to ensure correct functioning of the kmos kMC solver every action should have a corresponding condition for the same coordinate.

Now you might wonder, how come we can simply use m_CO and beta and such.
Well, that is because the evaluator will to some trickery to resolve such
terms. So beta will be first be translated into 1/(kboltzmann*T) and as
long as you have set a parameter `T` before, this will go through. Same
is true for m_CO, here the atomic masses are looked up and added. Note
that we need conversion factors of `bar` and `umass`.

Then the desorption process is almost the same, except the reverse::

  pt.add_process(name='CO_desorption',
                 conditions=[Condition(coord=coord, species='CO')],
                 actions=[Action(coord=coord, species='empty')],
                 rate_constant='p_CO*bar*A/sqrt(2*pi*umass*m_CO/beta)*exp(beta*deltaG*eV)')


To reduce typing, kmos also knows a shorthand notation for processes.
In order to produce the same process you could also type ::

  pt.parse_process('CO_desorption; CO@hollow->empty@hollow ; p_CO*bar*A/sqrt(2*pi*umass*m_CO/beta)*exp(beta*deltaG*eV)')

and since any non-existing on either the left or the right side
of the `->` symbol is replaced by a corresponding term with
the `default_species` (in this case `empty`) you could as
well type ::

  pt.parse_process('CO_desorption; CO@hollow->; p_CO*bar*A/sqrt(2*pi*umass*m_CO/beta)*exp(beta*deltaG*eV)')


and to make it even shorter you can parse and add the process on one line ::

  pt.parse_and_add_process('CO_desorption; CO@hollow->; p_CO*bar*A/sqrt(2*pi*umass*m_CO/beta)*exp(beta*deltaG*eV)')


In order to add processes on more than one site possible spanning across unit
cells, there is a shorthand as well. The full-fledged syntax for each
coordinate is ::

  name.offset.lattice

check :ref:`manual_coord_generation` for details.

Export, save, compile
^^^^^^^^^^^^^^^^^^^^^

Next, it's a good idea to save your work ::

  pt.filename = 'myfirst_kmc.xml'
  pt.save()

Now is the time to leave the python shell. In the current
directory you should see a `myfirst_kmc.xml`.
This XML file contains the full definition of your model
and you can create the source code and binaries in just one line.
So on the command line in the same directory as the XML file
you run ::

  kmos export myfirst_kmc.xml

or alternatively if you are still on the ipython shell
and don't like to quit it you can use the API hook
of the command line interface like ::

  import kmos.cli
  kmos.cli.main('export myfirst_kmc.xml')


Make sure this finishes gracefully without any line
containining an error.

If you now `cd` to that folder `myfirst_kmc` and run::

  kmos view

... and dada! Your first running kMC model right there!


If you wonder why the CO molecules are basically just dangling
there in mid-air that is because you have no background setup, yet.
Choose a transition metal of your choice and add it to the
lattice setup for extra credit :-).

Wondering where to go from here? If the work-flow makes
complete sense, you have a specific model in mind,
and just need some more idioms to implement it
I suggest you take a look at the `examples folder <https://github.com/mhoffman/kmos/tree/master/examples>`_.
for some hints. To learn more about the kmos approach
and methods you should into :ref:`topic guides <topic-guides>`.

Taking it home
^^^^^^^^^^^^^^^

Despite its simplicity you have now seen all elements needed
to implement a kMC model and hopefully gotten a first feeling for
the workflow.



.. [#proc_minilanguage]  You will have to describe all processes
                         in terms of  `conditions` and
                         `actions` and you find a more complete
                         description in the
                         :ref:`topic guide <proc_mini_language>`
                         to the process description syntax.

.. [#coord_minilanguage] The description of coordinates follows
                         the simple syntax of the coordinate
                         syntax and the
                         :ref:`topic guide <coord_mini_language>`
                         explains how that works.
