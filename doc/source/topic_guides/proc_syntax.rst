.. _proc_mini_language:

The Process Syntax
=========================


In kMC language a process is uniquely defined by a
configuration `before` the process is executed,
a configuration `after` the process is executed,
and a rate constant. Here this model is used to
define a process by giving it a :

- condition_list
- action_list
- rate_constant


As you might guess each `condition` corresponds to one 
`before`, and each `action` coresponds to one `after`.
In fact conditions and actions are actually of the same
class or data type: each condition and action consists of
a coordinate and a species which has to `be` or `will be` at
the coordinate.  This model of process definition also
means that each process in one unit cell has to be
defined explicitly.  Typically one a single crystal
surface one will have not one diffusion per species but
as many as there are equivalent directions :

  - species_diffusion_right
  - species_diffusion_up
  - species_diffusion_left
  - species_diffusion_down


while this seems like a lot of work to define that
many processes, it allows for a very clean and simple
definition of a process itself.  Later you can use 
geometric measures to abstract these cases as you will see
further down.

Adsorption
^^^^^^^^^^

Let's start with a very simple and basic process: molecular
adsorption of a gas phase species, let call it ``A`` on a
surface site. For this we need a species ::

  from kmos.types import *
  pt = Project()

  A = Species(name='A')
  pt.add_species(A)

  empty = Species(name='empty')
  pt.add_species(empty)


and the coordinate of a surface site ::

  layer = Layer(name='default')
  pt.add_layer(layer)
  layer.sites.append(Site(name='a'))
  coord = pt.lattice.generate_coord('a.(0,0,0).default')

which is for now all we need to define an adsorption
process::

  adsorption = Proces(name='adsorption_A_a',
                      condition_list=[Condition(coord=coord,
                                                species='empty')],
                      action_list=[Action(coord=coord,
                                          species='A')])
  pt.add_process(adsorption)

Now this wasn't hard, was it?


Diffusion
^^^^^^^^^

Let's move to another example, namely the `diffusion` of
a particle to the next unit cell in the y-direction.
You first need the coordinate of the final site ::

  final = pt.lattice.generate_coord('a.(0,1,0).default')

and you are good to go ::

  diffusion_up = Process('diffusion_A_up',
                         condition_list=[Condition(coord=coord, 
                                                   species='A'),
                                         Condition(coord=final,
                                                   species='empty')],
                         condition_list=[Condition(coord=coord, 
                                                   species='empty'),
                                         Condition(coord=final,
                                                   species='A')],
  pt.add_process(diffusion_up)

You can complicated this `ad infinitum` but you know all elements
needed to define processes.


Avoid Double Counting
^^^^^^^^^^^^^^^^^^^^^^^^

Finally a word of warning: `double counting` is a phenomenon
sometimes encountered for those process where there is more
than one equivalent direction for a process and the coordinates
within the process are also equivalent. Think of dissociative
oxygen adsorption. Novices typically collect all possible
directions (e.g. right, up, left, down) and then define this
process for each direction. Later they realize that in fact
they `double counted` the process because e.g. adsorption_up is
the same processes as adsorption_down, just executed from one
site above or below. Then they compensate by dividing each 
adsorption rate constant by 2. Later realizing that they
have to do the same for desorption. Ok, I have done this
and believe me it is really bad when you are looking for an
error if at the same you already divide the unit cell size
by 2 for some reason.

The smart way out is to save the pain and to avoid double
counting completely from the beginning and just think
how many process are geometrically inequivalent in the
unit cell. A simple trick is to only consider processes
in the `positive` directions.


Taking It Home
^^^^^^^^^^^^^^^

- A process consists of conditions, actions and a rate constant
- `double counting` is best avoided from the beginning
