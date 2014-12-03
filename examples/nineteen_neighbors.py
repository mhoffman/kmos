#!/usr/bin/env python


from kmos.types import Project, Condition, Action
from kmos.io import export_source
import numpy as np

N_sites = 14
N_directions = 24

pt = Project()
pt.set_meta(author='Your Name',
            email='your.name@server.com',
            model_name='MyFirstModel',
            model_dimension=3,)


pt.add_species(name='empty')
pt.add_species(name='Pt', representation="Atoms('Pt')")

layer = pt.add_layer(name='fcc')

coord = pt.lattice.generate_coord

layer.add_site(name='initial')
layer.add_site(name='final')

for i in range(N_sites):
    layer.add_site(name='site_%s' % i,)

# add one big process

condition_list = [Condition(
    coord=coord('site_%s' % i), species=['empty', 'Pt']) for i in range(N_sites)]
condition_list += [Condition(coord=coord('initial'), species='Pt'),
                   Condition(coord=coord('final'), species='empty')]

action_list = [Condition(coord=coord('initial'), species='empty'), Condition(
    coord=coord('final'), species='Pt')]


for direction in range(N_directions):
    pt.add_process(name='diffusion_%02d' % direction,
                   rate_constant='1.',
                   condition_list=condition_list,
                   action_list=action_list)

export_source(pt, export_dir='nineteen_neighbors', code_generator='lat_int2')
