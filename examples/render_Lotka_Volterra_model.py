#!/usr/bin/env python


import numpy as np
from kmos.types import Project, Site, Condition, Action

pt = Project()

pt.set_meta(author="LotkaVolterra",
            email='mjhoffmann@gmail.com',
            model_name='lotka_volterra_model',
            model_dimension=2)

pt.add_species(name='empty')
pt.add_species(name='A', representation="Atoms('O')")
pt.add_species(name='B', representation="Atoms('C')")

layer = pt.add_layer(name='sc')

pt.lattice.cell = np.diag([3.5, 3.5, 10])

layer.sites.append(Site(name='site', pos='.5 .5 .5'))


pt.add_parameter(name='k1', value='1000000.', adjustable=True, min=0., max=100.)
pt.add_parameter(name='k2', value=3.65, adjustable=True, min=0., max=100.)
pt.add_parameter(name='k3', value=1.1, adjustable=True, min=0., max=100.)
pt.add_parameter(name='zeta', value='0.06', adjustable=True, min=0., max=1.)



pt.parse_and_add_process('AA_creation1; A@site + empty@site.(1, 0, 0) -> A@site + A@site.(1,0,0); k1')
pt.parse_and_add_process('AA_creation2; A@site + empty@site.(-1, 0, 0) -> A@site + A@site.(-1,0,0); k1')
pt.parse_and_add_process('AA_creation3; A@site + empty@site.(0, 1, 0) -> A@site + A@site.(0,1,0); k1')
pt.parse_and_add_process('AA_creation4; A@site + empty@site.(0, -1, 0) -> A@site + A@site.(0,-1,0); k1')

pt.parse_and_add_process('AB_reaction1; A@site + B@site.(1, 0, 0) -> B@site + B@site.(1,0,0); k2')
pt.parse_and_add_process('AB_reaction2; A@site + B@site.(-1, 0, 0) -> B@site + B@site.(-1,0,0); k2')
pt.parse_and_add_process('AB_reaction3; A@site + B@site.(0, 1, 0) -> B@site + B@site.(0,1,0); k2')
pt.parse_and_add_process('AB_reaction4; A@site + B@site.(0, -1, 0) -> B@site + B@site.(0,-1,0); k2')

# add really slow reverse processes just to keep the model from crashing
pt.parse_and_add_process('B_desorption; B@site -> empty@site; k3')

pt.print_statistics()
pt.save('Lotka_Volterra_model.xml')
