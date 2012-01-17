#!/usr/bin/env python

from ase.lattice.surface import fcc111
import ase
from kmos.utils import get_ase_constructor
from kmos.types import *
import numpy as np


slab = fcc111('Pt', [1,1,4], vacuum=10)
#ase.visualize.view(slab)

positions = slab.positions
pt = Project()
pt.set_meta(model_name='pt111',
            model_dimension='2',
            author='Max J. Hoffmann',
            email='mjhoffmann@gmail.com',
            debug=0)

pt.lattice.representation = get_ase_constructor(slab)
pt.lattice.cell = slab.cell
layer = Layer(name='pt111')
pos1 = [positions[1, 0], positions[1, 1], 24]
layer.add_site(Site(name='hollow1',
                    pos=np.linalg.solve(slab.cell, pos1)))

pos2 = [positions[2, 0], positions[2, 1], 24]
layer.add_site(Site(name='hollow2',
                    pos=np.linalg.solve(slab.cell, pos2)))

pt.add_layer(layer)
pt.lattice.representation = '[%s]' % get_ase_constructor(slab)


# Add species
pt.add_species(name='empty', color='#ffffff')
pt.add_species(name='H', representation="Atoms('H')", color='#ffff00')

#Add Processes
pt.parse_process('H_adsorption_hollow1; ->H@hollow1; 100000')
pt.parse_process('H_adsorption_hollow2; ->H@hollow2; 100000')

pt.parse_process('H_desorption_hollow1; H@hollow1->; 100000')
pt.parse_process('H_desorption_hollow2; H@hollow2->; 100000')

# Export, Save
xmlfile = file('Pt_111.xml', 'w')
xmlfile.write(str(pt))
xmlfile.close()
