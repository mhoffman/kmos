.. _proc_mini_language:

The Process Syntax
=========================


A process in kMC language can be uniquely defined by a
configuration that has to exist `before` the process,
a configuration `after` the process is executed,
and a rate constant. Here we use this model for the
description of a process by giving each process a :
- condition_list
- action_list
- rate_constant


As you might guess each `condition` corresponds to one 
`before`, and each `action` coresponds to one `after`.
In fact conditions and actions are actually of the same
class: each condition and action consists of a coordinate
and a species which has to be or will be at the coordinate.
This model of process definition also means that each
process in one unit cell has to be defined explicitly.
So typically one a single crystal surface one
will have not one diffusion per species but as many
as there are degenerate direction :
  - species_diffusion_right
  - species_diffusion_up
  - species_diffusion_left
  - species_diffusion_down


while this seems like a lot of work, it allows for
a very clean definition and you can use things like
distance measure to abstract these case as you will see
further down.

Let's start with a very simple and basic process: molecular
adsorption of a gas phase species, let call it ``A`` on a surface site. For this
we need a species ::

  from kmos.types import *
  species = Species(name='A')

and the coordinate of a surface site ::

  pt = Project()
  layer = Layer(name='default')
  pt.add_layer(layer)
  layer.sites.append(Site(name='a'))
  coord = pt.lattice.generate_coord('a.(0,0,0).default')
