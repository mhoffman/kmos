#!/usr/bin/env python

from kmos.types import *

def main():

    pt = Project()
# Meta
    pt.meta.author = 'Max J. Hoffmann'
    pt.meta.email = 'mjhoffmann@gmail.com'
    pt.meta.model_name = 'AB_no_diffusion'
    pt.meta.model_dimension = 2
    pt.meta.debug = 0


# add species
    pt.add_species(name='empty')
    pt.add_species(name='A', representation="Atoms('O')")
    pt.add_species(name='B', representation="Atoms('CO', [[0,0,0],[0,0,1.2]])")

# add sites/layer
    layer = Layer(name='default')
    layer.sites.append(Site(name='a'))
    pt.add_layer(layer)
    pt.species_list.default_species = 'empty'


# add parameter
    parameters = {}
    parameters['p_COgas'] = {'value':1., 'adjustable':True,
                                         'min':1.e-13, 'max':1.e2,
                                         'scale':'log'}
    parameters['p_O2gas'] = {'value':1., 'adjustable':True,
                                         'min':1.e-13, 'max':1.e2,
                                         'scale':'log'}
    parameters['T'] = {'value':600}
    parameters['A'] = {'value':1.552e-19}
    parameters['E_bind_O2'] = {'value':-2.138}
    parameters['E_bind_CO'] = {'value':-1.9}
    parameters['E_react'] = {'value': 0.9}


    for key, value in parameters.iteritems():
        pt.add_parameter(name=key, **value)


    coord = pt.lattice.generate_coord('a.(0,0,0).default')
    up = pt.lattice.generate_coord('a.(0,1,0).default')
    right = pt.lattice.generate_coord('a.(1,0,0).default')
    down = pt.lattice.generate_coord('a.(0,-1,0).default')
    left = pt.lattice.generate_coord('a.(-1,0,0).default')

    pt.add_process(name='A_adsorption',
                   rate_constant='p_O2gas*bar*A/sqrt(2*pi*m_O2*umass/beta)',
                   condition_list=[Condition(coord=coord, species='empty')],
                   action_list=[Action(coord=coord, species='A')],)

    pt.add_process(name='A_desorption',
                   rate_constant='p_O2gas*bar*A/sqrt(2*pi*m_O2*umass/beta)*exp(beta*(E_bind_O2-mu_O2gas)*eV)',
                   condition_list=[Condition(coord=coord, species='A')],
                   action_list=[Action(coord=coord, species='empty')],)

    pt.add_process(name='B_adsorption',
                   rate_constant='p_COgas*bar*A/sqrt(2*pi*m_CO*umass/beta)',
                   condition_list=[Condition(coord=coord, species='empty')],
                   action_list=[Action(coord=coord, species='B')],)

    pt.add_process(name='B_desorption',
                   rate_constant='p_COgas*bar*A/sqrt(2*pi*m_CO*umass/beta)*exp(beta*(E_bind_CO-mu_COgas)*eV)',
                   condition_list=[Condition(coord=coord, species='B')],
                   action_list=[Condition(coord=coord, species='empty')],)

    for neighbor, name in [(right, 'right'),
                           (left, 'left'),
                           (up, 'up'),
                           (down, 'down')]:
        pt.add_process(name='AB_react_%s' % name,
                       rate_constant='1/(beta*h)*exp(-beta*E_react*eV)',
                       condition_list=[Condition(coord=coord, species='A'),
                                       Condition(coord=neighbor, species='B')],
                       action_list=[Action(coord=coord, species='empty'),
                                   Action(coord=neighbor, species='empty')],
                       tof_count={'TOF':1})


    return pt

if __name__ == '__main__':
    pt = main()
    pt.save('AB_model.ini')

