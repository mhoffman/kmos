#!/usr/bin/env python

from kmos.types import *
from kmos.io import *
import numpy as np


pt = Project()
# Meta information
pt.set_meta(author='Max J. Hoffmann',
            email='mjhoffmann@gmail.com',
            model_name='ion_diffusion_model',
            model_dimension=2)

# Species
pt.add_species(name='empty',)
pt.add_species(name='source',
               representation="Atoms('Au')")
pt.add_species(name='drain',
               representation="Atoms('Ag')")
pt.add_species(name='blocked',
               representation="Atoms('C')")
pt.add_species(name='ion',
               representation="Atoms('Si')")
pt.species_list.default_species = 'empty'

# Layers
layer = Layer(name='default')
layer.sites.append(Site(name='a', pos='0.5 0.5 0.5',
                        default_species='empty'))
pt.add_layer(layer)
pt.lattice.cell = np.diag([3, 3, 3])

# Parameters
pt.add_parameter(name='k_up', value=1e4, adjustable=True, min=1, max=1.e6, scale='log')
pt.add_parameter(name='k_down', value=1e3, adjustable=True, min=1, max=1.e6, scale='log')
pt.add_parameter(name='k_left', value=1e3, adjustable=True, min=1, max=1.e6, scale='log')
pt.add_parameter(name='k_right', value=1e3, adjustable=True, min=1, max=1.e6, scale='log')
pt.add_parameter(name='k_entry', value=1e3, adjustable=True, min=1, max=1.e6, scale='log')
pt.add_parameter(name='k_exit', value=1e3, adjustable=True, min=1, max=1.e6, scale='log')

# Coords
center = pt.lattice.generate_coord('a.(0,0,0).default')

up = pt.lattice.generate_coord('a.(0,1,0).default')
down = pt.lattice.generate_coord('a.(0,-1,0).default')

left = pt.lattice.generate_coord('a.(-1,0,0).default')
right = pt.lattice.generate_coord('a.(1,0,0).default')

# Processes
pt.add_process(name='diffusion_up',
               conditions=[Condition(species='ion', coord=center),
                           Condition(species='empty', coord=up)],
               actions=[Action(species='ion', coord=up),
                        Action(species='empty', coord=center)],
               rate_constant='k_up')

pt.add_process(name='diffusion_down',
               conditions=[Condition(species='ion', coord=center),
                           Condition(species='empty', coord=down)],
               actions=[Action(species='ion', coord=down),
                        Action(species='empty', coord=center)],
               rate_constant='k_down')
pt.add_process(name='diffusion_left',
               conditions=[Condition(species='ion', coord=center),
                           Condition(species='empty', coord=left)],
               actions=[Action(species='ion', coord=left),
                        Action(species='empty', coord=center)],
               rate_constant='k_left')
pt.add_process(name='diffusion_right',
               conditions=[Condition(species='ion', coord=center),
                           Condition(species='empty', coord=right)],
               actions=[Action(species='ion', coord=right),
                        Action(species='empty', coord=center)],
               rate_constant='k_right')

pt.add_process(name='entry',
               conditions=[Condition(species='empty', coord=center),
                           Condition(species='source', coord=down)],
               actions=[Action(species='ion', coord=center),
                        Action(species='source', coord=down)],
               rate_constant='k_entry')
pt.add_process(name='exit',
               conditions=[Condition(species='ion', coord=center),
                           Condition(species='drain', coord=up)],
               actions=[Action(species='empty', coord=center),
                        Action(species='drain', coord=up)],
               rate_constant='k_exit')

# Export
pt.export_xml_file('diffusion_model.xml')
