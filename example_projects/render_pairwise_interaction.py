#!/usr/bin/env python

from kmos.types import *
from itertools import product
import numpy as np

pt = Project()
pt.set_meta(author='Max J. Hoffmann',
            email='mjhoffmann@gmail.com',
            model_name='dummy_pairwise_interaction',
            model_dimension=2)

layer = pt.add_layer(name='simplecubic_2d')
layer.add_site(name='a')
pt.add_species(name='empty', color='#ffffff')
pt.add_species(name='CO', color='#000000', representation="Atoms('CO',[[0,0,0],[0,0,1.2]])")
pt.add_parameter(name='E_CO', value=-1)
pt.add_parameter(name='E_CO_nn', value=.2)
pt.add_parameter(name='p_CO', value=.2)
pt.add_parameter(name='T', value=600)
pt.add_parameter(name='A', value='(3*angstrom)**2')

center = pt.lattice.generate_coord('a')

A = 1.  # lattice const.


pt.lattice.cell = np.diag([A, A, 10])

# Adsorption process
pt.add_process(name='CO_adsorption',
               conditions=[Condition(species='empty', coord=center)],
               actions=[Action(species='CO', coord=center)],
               rate_constant='p_CO*A/sqrt(2*m_CO/beta)')

# fetch a lot of coordinates
coords = pt.lattice.generate_coord_set(size=[2, 2, 2],
                                       layer_name='simplecubic_2d')

# fetch all nearest neighbor coordinates
nn_coords = [nn_coord for i, nn_coord in enumerate(coords)
             if 0 < (np.linalg.norm(nn_coord.pos - center.pos)) <= A]

# produce all desorption processes
# using pair nearest-neighbor
# interaction
for i, nn_config in enumerate(product(['empty', 'CO'], repeat=len(nn_coords))):
    # Number of CO atoms in neighborhood
    N_CO = nn_config.count('CO')

    # rate constant with pairwise interaction
    rate_constant = 'p_CO*A/sqrt(2*m_CO/beta)*exp(beta*(E_CO+%s*E_CO_nn)*eV)' % N_CO

    # turn neighborhood into conditions using zip
    conditions = [Condition(coord=coord, species=species)
                  for coord, species in zip(nn_coords, nn_config)]

    # And the central site
    conditions += [Condition(species='CO', coord=center)]

    # The action: central site is empty
    actions = [Action(species='empty', coord=center)]

    pt.add_process(name='CO_desorption_%s' % i,
                   conditions=conditions,
                   actions=actions,
                   rate_constant=rate_constant)

pt.filename = 'pairwise_interaction.xml'
pt.save()  # Done
