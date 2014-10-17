#!/usr/bin/env python


import numpy as np
from kmos.types import Project, Site, Condition, Action

pt = Project()

pt.set_meta(author="Ziff,Gulari,Barshad",
            email='mjhoffmann@gmail.com',
            model_name='zgb_model',
            model_dimension=2)

pt.add_species(name='empty', color='#ffffff')
pt.add_species(name='CO', representation="Atoms('C')", color='#000000')
pt.add_species(name='O', representation="Atoms('O')", color='#ff0000')

layer = pt.add_layer(name='sc')

pt.lattice.cell = np.diag([3.5, 3.5, 10])

layer.sites.append(Site(name='site', pos='.5 .5 .5'))

pt.add_parameter(name='yCO', value='0.45', adjustable=True, min=0., max=1.)

pt.parse_and_add_process('CO_adsorption; empty@site -> CO@site; yCO')

pt.parse_and_add_process('O2_adsorption1; empty@site + empty@site.(1, 0, 0) -> O@site + O@site.(1,0,0); (1 - yCO)/2.')
pt.parse_and_add_process('O2_adsorption2; empty@site + empty@site.(0, 1, 0) -> O@site + O@site.(0,1,0); (1 - yCO)/2.')

pt.parse_and_add_process('CO_oxidation1; CO@site + O@site.(1, 0, 0) -> empty@site + empty@site.(1,0,0); 10**10')
pt.parse_and_add_process('CO_oxidation3; CO@site + O@site.(-1, 0, 0) -> empty@site + empty@site.(-1,0,0); 10**10')
pt.parse_and_add_process('CO_oxidation2; CO@site + O@site.(0, 1, 0) -> empty@site + empty@site.(0,1,0); 10**10')
pt.parse_and_add_process('CO_oxidation4; CO@site + O@site.(0, -1, 0) -> empty@site + empty@site.(0,-1,0); 10**10')


# add really slow reverse processes just to keep the model from crashing
pt.parse_and_add_process('CO_desorption; CO@site -> empty@site; 1e-13')
pt.parse_and_add_process('O2_desorption1; O@site + O@site.(1, 0, 0) -> empty@site + empty@site.(1,0,0); 1e-13')
pt.parse_and_add_process('O2_desorption2; O@site + O@site.(0, 1, 0) -> empty@site + empty@site.(0,1,0); 1e-13')

pt.print_statistics()
pt.save('ZGB_model.xml')
