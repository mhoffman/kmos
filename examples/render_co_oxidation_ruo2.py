#!/usr/bin/env python

#DISCLAIMER: this is hacked down really quickly
#BEWARE OF BUGS

from kmos.types import *
from kmos.io import *
import numpy as np

pt = Project()

pt.set_meta(author='Max J. Hoffmann',
            email='mjhoffmann@gmail.com',
            model_name='CO_oxidation_Ruo2',
            model_dimension=2)

# Species
pt.add_species(name='empty', color='#ffffff')
pt.add_species(name='CO',
               color='#000000',
               representation="Atoms('CO',[[0,0,0],[0,0,1.2]])")
pt.add_species(name='O',
               color='#ff0000',
               representation="Atoms('O')")

# Layer/Sites
layer = Layer(name='ruo2')
layer.sites.append(Site(name='bridge', pos='0.0 0.5 0.7'))
layer.sites.append(Site(name='cus', pos='0.5 0.5 0.7'))

pt.add_layer(layer)

pt.lattice.representation = """[
Atoms(symbols='O2Ru2',
          pbc=np.array([False, False, False], dtype=bool),
          cell=np.array(
      [[  6.39 ,   0.   ,   0.   ],
       [  0.   ,   3.116,   0.   ],
       [  0.   ,   0.   ,  20.   ]]),
          positions=np.array(
      [[  4.435981  ,   0.        ,  12.7802862 ],
       [  1.95416379,   0.        ,  12.7802862 ],
       [  0.        ,   0.        ,  12.7802862 ],
       [  3.1950724 ,   1.5582457 ,  12.7802862 ]]))

]"""
pt.lattice.cell = np.diag([6.43, 3.12, 20])

# Parameters

pt.add_parameter(name='p_COgas', value=1, adjustable=True, min=1e-13, max=1e2,
                 scale='log')
pt.add_parameter(name='p_O2gas', value=1, adjustable=True, min=1e-13, max=1e2,
                 scale='log')
pt.add_parameter(name='T', value=450, adjustable=True, min=300, max=1500)

pt.add_parameter(name='A', value='%s*angstrom**2' % (pt.lattice.cell[0,0]*
                                                      pt.lattice.cell[1,1]))
pt.add_parameter(name='E_O_bridge', value=-2.3)
pt.add_parameter(name='E_O_cus', value=-1.0)
pt.add_parameter(name='E_CO_bridge', value=-1.6)
pt.add_parameter(name='E_CO_cus', value=-1.3)


pt.add_parameter(name='E_react_Ocus_COcus', value=0.9)
pt.add_parameter(name='E_react_Ocus_CObridge', value=1.2)
pt.add_parameter(name='E_react_Obridge_COcus', value=0.8)
pt.add_parameter(name='E_react_Obridge_CObridge', value=1.5)


pt.add_parameter(name='E_COdiff_cus_cus', value=1.7)
pt.add_parameter(name='E_COdiff_cus_bridge', value=1.3)
pt.add_parameter(name='E_COdiff_bridge_bridge', value=0.6)
pt.add_parameter(name='E_COdiff_bridge_cus', value=1.6)


pt.add_parameter(name='E_Odiff_cus_cus', value=1.6)
pt.add_parameter(name='E_Odiff_bridge_bridge', value=0.7)
pt.add_parameter(name='E_Odiff_bridge_cus', value=2.3)
pt.add_parameter(name='E_Odiff_cus_bridge', value=1.0)


# Coordinates

cus = pt.lattice.generate_coord('cus.(0,0,0).ruo2')
cus_right = pt.lattice.generate_coord('bridge.(1,0,0).ruo2')
cus_left = pt.lattice.generate_coord('bridge.(0,0,0).ruo2')

cus_up = pt.lattice.generate_coord('cus.(0,1,0).ruo2')
cus_down = pt.lattice.generate_coord('cus.(0,-1,0).ruo2')

bridge = pt.lattice.generate_coord('bridge.(0,0,0).ruo2')
bridge_right = pt.lattice.generate_coord('cus.(0,0,0).ruo2')
bridge_left = pt.lattice.generate_coord('cus.(-1,0,0).ruo2')

bridge_up = pt.lattice.generate_coord('bridge.(0,1,0).ruo2')
bridge_down = pt.lattice.generate_coord('bridge.(0,-1,0).ruo2')

# Processes

# CO Adsorption/Desorption
pt.add_process(name='CO_adsorption_cus',
               conditions=[Condition(species='empty', coord=cus)],
               actions=[Action(species='CO', coord=cus)],
               rate_constant='p_COgas*bar*A/2/sqrt(2*pi*umass*m_CO/beta)')
pt.add_process(name='CO_desorption_cus',
               conditions=[Condition(species='CO', coord=cus)],
               actions=[Action(species='empty', coord=cus)],
               rate_constant='p_COgas*bar*A/2/sqrt(2*pi*umass*m_CO/beta)*exp(beta*(E_CO_cus-mu_COgas)*eV)')

pt.add_process(name='CO_adsorption_bridge',
               conditions=[Condition(species='empty', coord=bridge)],
               actions=[Action(species='CO', coord=bridge)],
               rate_constant='p_COgas*bar*A/2/sqrt(2*pi*umass*m_CO/beta)')
pt.add_process(name='CO_desorption_bridge',
               conditions=[Condition(species='CO', coord=bridge)],
               actions=[Action(species='empty', coord=bridge)],
               rate_constant='p_COgas*bar*A/2/sqrt(2*pi*umass*m_CO/beta)*exp(beta*(E_CO_bridge-mu_COgas)*eV)')

# CO diffusion

# cus/cus
pt.add_process(name='COdiff_cus_up',
               conditions=[Condition(species='CO', coord=cus),
                           Condition(species='empty', coord=cus_up)],
               actions=[Condition(species='empty', coord=cus),
                        Condition(species='CO', coord=cus_up)],
                rate_constant='(beta*h)**(-1)*exp(-beta*(E_COdiff_cus_cus)*eV)')

pt.add_process(name='COdiff_cus_down',
               conditions=[Condition(species='CO', coord=cus),
                           Condition(species='empty', coord=cus_down)],
               actions=[Condition(species='empty', coord=cus),
                        Condition(species='CO', coord=cus_down)],
                rate_constant='(beta*h)**(-1)*exp(-beta*(E_COdiff_cus_cus)*eV)')


# bridge/bridge
pt.add_process(name='COdiff_bridge_up',
               conditions=[Condition(species='CO', coord=bridge),
                           Condition(species='empty', coord=bridge_up)],
               actions=[Condition(species='empty', coord=bridge),
                        Condition(species='CO', coord=bridge_up)],
                rate_constant='(beta*h)**(-1)*exp(-beta*(E_COdiff_bridge_bridge)*eV)')
pt.add_process(name='COdiff_bridge_down',
               conditions=[Condition(species='CO', coord=bridge),
                           Condition(species='empty', coord=bridge_down)],
               actions=[Condition(species='empty', coord=bridge),
                        Condition(species='CO', coord=bridge_down)],
                rate_constant='(beta*h)**(-1)*exp(-beta*(E_COdiff_bridge_bridge)*eV)')
# bridge/cus
pt.add_process(name='COdiff_bridge_right',
               conditions=[Condition(species='CO', coord=bridge),
                           Condition(species='empty', coord=bridge_right)],
               actions=[Condition(species='empty', coord=bridge),
                        Condition(species='CO', coord=bridge_right)],
                rate_constant='(beta*h)**(-1)*exp(-beta*(E_COdiff_bridge_cus)*eV)')

pt.add_process(name='COdiff_bridge_left',
               conditions=[Condition(species='CO', coord=bridge),
                           Condition(species='empty', coord=bridge_left)],
               actions=[Condition(species='empty', coord=bridge),
                        Condition(species='CO', coord=bridge_left)],
                rate_constant='(beta*h)**(-1)*exp(-beta*(E_COdiff_bridge_cus)*eV)')

# bridge/cus
pt.add_process(name='COdiff_cus_left',
               conditions=[Condition(species='CO', coord=cus),
                           Condition(species='empty', coord=cus_left)],
               actions=[Condition(species='empty', coord=cus),
                        Condition(species='CO', coord=cus_left)],
                rate_constant='(beta*h)**(-1)*exp(-beta*(E_COdiff_cus_bridge)*eV)')

pt.add_process(name='COdiff_cus_right',
               conditions=[Condition(species='CO', coord=cus),
                           Condition(species='empty', coord=cus_right)],
               actions=[Condition(species='empty', coord=cus),
                        Condition(species='CO', coord=cus_right)],
                rate_constant='(beta*h)**(-1)*exp(-beta*(E_COdiff_cus_bridge)*eV)')





# O2 Adsorption/Desorption
# avoiding double-counting ...
pt.add_process(name='O2_adsorption_cus_up',
               conditions=[Condition(species='empty', coord=cus),
                        Condition(species='empty', coord=cus_up),],
               actions=[Condition(species='O', coord=cus),
                        Condition(species='O', coord=cus_up),],
               rate_constant='p_O2gas*bar*A/sqrt(2*pi*umass*m_O2/beta)')

pt.add_process(name='O2_desorption_cus_up',
               conditions=[Condition(species='O', coord=cus),
                        Condition(species='O', coord=cus_up),],
               actions=[Condition(species='empty', coord=cus),
                        Condition(species='empty', coord=cus_up),],
               rate_constant='p_O2gas*bar*A/sqrt(2*pi*umass*m_O2/beta)*exp(beta*(2*E_O_cus-mu_O2gas)*eV)')

pt.add_process(name='O2_adsorption_cus_right',
               conditions=[Condition(species='empty', coord=cus),
                        Condition(species='empty', coord=cus_right),],
               actions=[Condition(species='O', coord=cus),
                        Condition(species='O', coord=cus_right),],
               rate_constant='p_O2gas*bar*A/sqrt(2*pi*umass*m_O2/beta)')

pt.add_process(name='O2_desorption_cus_right',
               conditions=[Condition(species='O', coord=cus),
                        Condition(species='O', coord=cus_right),],
               actions=[Condition(species='empty', coord=cus),
                        Condition(species='empty', coord=cus_right),],
               rate_constant='p_O2gas*bar*A/sqrt(2*pi*umass*m_O2/beta)*exp(beta*((E_O_cus+E_O_bridge)-mu_O2gas)*eV)')

pt.add_process(name='O2_adsorption_bridge_up',
               conditions=[Condition(species='empty', coord=bridge),
                        Condition(species='empty', coord=bridge_up),],
               actions=[Condition(species='O', coord=bridge),
                        Condition(species='O', coord=bridge_up),],
               rate_constant='p_O2gas*bar*A/sqrt(2*pi*umass*m_O2/beta)')

pt.add_process(name='O2_desorption_bridge_up',
               conditions=[Condition(species='O', coord=bridge),
                        Condition(species='O', coord=bridge_up),],
               actions=[Condition(species='empty', coord=bridge),
                        Condition(species='empty', coord=bridge_up),],
               rate_constant='p_O2gas*bar*A/sqrt(2*pi*umass*m_O2/beta)*exp(beta*(2*E_O_bridge-mu_O2gas)*eV)')

pt.add_process(name='O2_adsorption_bridge_right',
               conditions=[Condition(species='empty', coord=bridge),
                        Condition(species='empty', coord=bridge_right),],
               actions=[Condition(species='O', coord=bridge),
                        Condition(species='O', coord=bridge_right),],
               rate_constant='p_O2gas*bar*A/sqrt(2*pi*umass*m_O2/beta)')

pt.add_process(name='O2_desorption_bridge_right',
               conditions=[Condition(species='O', coord=bridge),
                        Condition(species='O', coord=bridge_right),],
               actions=[Condition(species='empty', coord=bridge),
                        Condition(species='empty', coord=bridge_right),],
               rate_constant='p_O2gas*bar*A/sqrt(2*pi*umass*m_O2/beta)*exp(beta*((E_O_bridge+E_O_cus)-mu_O2gas)*eV)')


# O diffusion

# cus/cus
pt.add_process(name='Odiff_cus_up',
               conditions=[Condition(species='O', coord=cus),
                           Condition(species='empty', coord=cus_up)],
               actions=[Condition(species='empty', coord=cus),
                        Condition(species='O', coord=cus_up)],
                rate_constant='(beta*h)**(-1)*exp(-beta*(E_Odiff_cus_cus)*eV)')

pt.add_process(name='Odiff_cus_down',
               conditions=[Condition(species='O', coord=cus),
                           Condition(species='empty', coord=cus_down)],
               actions=[Condition(species='empty', coord=cus),
                        Condition(species='O', coord=cus_down)],
                rate_constant='(beta*h)**(-1)*exp(-beta*(E_Odiff_cus_cus)*eV)')


# bridge/bridge
pt.add_process(name='Odiff_bridge_up',
               conditions=[Condition(species='O', coord=bridge),
                           Condition(species='empty', coord=bridge_up)],
               actions=[Condition(species='empty', coord=bridge),
                        Condition(species='O', coord=bridge_up)],
                rate_constant='(beta*h)**(-1)*exp(-beta*(E_Odiff_bridge_bridge)*eV)')
pt.add_process(name='Odiff_bridge_down',
               conditions=[Condition(species='O', coord=bridge),
                           Condition(species='empty', coord=bridge_down)],
               actions=[Condition(species='empty', coord=bridge),
                        Condition(species='O', coord=bridge_down)],
                rate_constant='(beta*h)**(-1)*exp(-beta*(E_Odiff_bridge_bridge)*eV)')
# bridge/cus
pt.add_process(name='Odiff_bridge_right',
               conditions=[Condition(species='O', coord=bridge),
                           Condition(species='empty', coord=bridge_right)],
               actions=[Condition(species='empty', coord=bridge),
                        Condition(species='O', coord=bridge_right)],
                rate_constant='(beta*h)**(-1)*exp(-beta*(E_Odiff_bridge_cus)*eV)')

pt.add_process(name='Odiff_bridge_left',
               conditions=[Condition(species='O', coord=bridge),
                           Condition(species='empty', coord=bridge_left)],
               actions=[Condition(species='empty', coord=bridge),
                        Condition(species='O', coord=bridge_left)],
                rate_constant='(beta*h)**(-1)*exp(-beta*(E_Odiff_bridge_cus)*eV)')

# bridge/cus
pt.add_process(name='Odiff_cus_left',
               conditions=[Condition(species='O', coord=cus),
                           Condition(species='empty', coord=cus_left)],
               actions=[Condition(species='empty', coord=cus),
                        Condition(species='O', coord=cus_left)],
                rate_constant='(beta*h)**(-1)*exp(-beta*(E_Odiff_cus_bridge)*eV)')

pt.add_process(name='Odiff_cus_right',
               conditions=[Condition(species='O', coord=cus),
                           Condition(species='empty', coord=cus_right)],
               actions=[Condition(species='empty', coord=cus),
                        Condition(species='O', coord=cus_right)],
                rate_constant='(beta*h)**(-1)*exp(-beta*(E_Odiff_cus_bridge)*eV)')


# Reaction
pt.add_process(name='React_cus_up',
               conditions=[Condition(species='O', coord=cus),
                           Condition(species='CO', coord=cus_up)],
               actions=[Action(species='empty', coord=cus),
                        Action(species='empty', coord=cus_up)],
                rate_constant='(beta*h)**(-1)*exp(-beta*E_react_Ocus_COcus*eV)',
                tof_count={'CO_oxidation':1})

pt.add_process(name='React_cus_down',
               conditions=[Condition(species='O', coord=cus),
                           Condition(species='CO', coord=cus_down)],
               actions=[Action(species='empty', coord=cus),
                        Action(species='empty', coord=cus_down)],
                rate_constant='(beta*h)**(-1)*exp(-beta*E_react_Ocus_COcus*eV)',
                tof_count={'CO_oxidation':1})

pt.add_process(name='React_cus_right',
               conditions=[Condition(species='O', coord=cus),
                           Condition(species='CO', coord=cus_right)],
               actions=[Action(species='empty', coord=cus),
                        Action(species='empty', coord=cus_right)],
                rate_constant='(beta*h)**(-1)*exp(-beta*E_react_Ocus_CObridge*eV)',
                tof_count={'CO_oxidation':1})

pt.add_process(name='React_cus_left',
               conditions=[Condition(species='O', coord=cus),
                           Condition(species='CO', coord=cus_left)],
               actions=[Action(species='empty', coord=cus),
                        Action(species='empty', coord=cus_left)],
                rate_constant='(beta*h)**(-1)*exp(-beta*E_react_Ocus_CObridge*eV)',
                tof_count={'CO_oxidation':1})

pt.add_process(name='React_bridge_up',
               conditions=[Condition(species='O', coord=bridge),
                           Condition(species='CO', coord=bridge_up)],
               actions=[Action(species='empty', coord=bridge),
                        Action(species='empty', coord=bridge_up)],
                rate_constant='(beta*h)**(-1)*exp(-beta*E_react_Obridge_CObridge*eV)',
                tof_count={'CO_oxidation':1})
pt.add_process(name='React_bridge_down',
               conditions=[Condition(species='O', coord=bridge),
                           Condition(species='CO', coord=bridge_down)],
               actions=[Action(species='empty', coord=bridge),
                        Action(species='empty', coord=bridge_down)],
                rate_constant='(beta*h)**(-1)*exp(-beta*E_react_Obridge_CObridge*eV)',
                tof_count={'CO_oxidation':1})
pt.add_process(name='React_bridge_right',
               conditions=[Condition(species='O', coord=bridge),
                           Condition(species='CO', coord=bridge_right)],
               actions=[Action(species='empty', coord=bridge),
                        Action(species='empty', coord=bridge_right)],
                rate_constant='(beta*h)**(-1)*exp(-beta*E_react_Obridge_COcus*eV)',
                tof_count={'CO_oxidation':1})

pt.add_process(name='React_bridge_left',
               conditions=[Condition(species='O', coord=bridge),
                           Condition(species='CO', coord=bridge_left)],
               actions=[Action(species='empty', coord=bridge),
                        Action(species='empty', coord=bridge_left)],
                rate_constant='(beta*h)**(-1)*exp(-beta*E_react_Obridge_COcus*eV)',
                tof_count={'CO_oxidation':1})

pt.save('CO_oxidation.ini')
pt.save('CO_oxidation.xml')
pt.print_statistics()
