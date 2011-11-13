#!/usr/bin/env python
import pdb

from kmos.io import *
from kmos.types import *
import kmos
import numpy as np
import kmos.utils
from ase.atoms import Atoms
import ase.io.castep
import os





DEFAULT_LAYER = 'Pd100'

class ModelBuilder(object):
    def __init__(self):
        self.pt = Project()

    def standard_build(self):
        self.set_meta()
        self.set_lattice()
        self.set_layers()
        self.set_parameters()
        self.set_species()
        self.set_processes()



    def pd100_build(self):
        self.set_meta()
        self.set_lattice()
        self.set_layers()
        new_pos = (self.atoms.positions[3]-self.y +self.atoms.positions[0])/2
        self.atoms += ase.atoms.Atoms('Pd',[new_pos])
        self.pt.layer_list.set_representation(self.atoms)

        new_sites = [['bridge7', self.atoms.positions[[2,14]].mean(axis=0)],
                     ['bridge8', self.atoms.positions[[3,14]].mean(axis=0)],
                     ['bridge9', self.atoms.positions[[1,14]].mean(axis=0)+(-self.y+self.x)/2],
                     ['bridge10', self.atoms.positions[[0,14]].mean(axis=0)-self.y/2]]

        for name, pos in new_sites:
            pos = np.linalg.solve(self.atoms.cell, pos)
            self.pt.layer_list[0].sites.append(Site(name=name,
                                             default_species='empty',
                                             layer=DEFAULT_LAYER,
                                             tags='weakbridge CO',
                                             pos=pos))
        self.coord_set = self.pt.layer_list.generate_coord_set(size=[3, 3, 1],
                                                               layer_name=DEFAULT_LAYER)
        self.set_species()
        self.set_parameters()

        # processes
        self.set_co_adsorption_desorption()
        self.set_co_diffusion()
        self.set_o2_adsorption_desorption()
        self.set_o_diffusion()
        self.set_reaction()



    def export(self, filename):
        export_xml(self.pt, filename)

    def print_statistics(self):
        print('Statistics\n-------------')
        for process_type in ['CO_adsorption', 'CO_desorption', 'CO_diffusion',
                             'O2_adsorption', 'O2_desorption', 'O_diffusion',
                             'Reaction']:
            nprocs = len([x for x in self.pt.get_processes() if x.name.startswith(process_type)])
            print('\t- %s : %s' % (process_type, nprocs))

    def set_meta(self):
        # Meta
        self.pt.meta.author = 'Max J. Hoffmann'
        self.pt.meta.email = 'mjhoffmann@gmail.com'
        self.pt.meta.model_dimension = '2'
        self.pt.meta.model_name = 'Pdsqrt5'
        self.pt.meta.debug = '0'

    def set_lattice(self):
        # Lattice / Layer
        self.atoms = ase.io.castep.read_seed('substrate_2layers')
        cell = tuple(self.atoms.cell.diagonal())

        self.pt.layer_list.default_layer = DEFAULT_LAYER
        self.pt.layer_list.cell = self.atoms.cell
        self.pt.layer_list.set_representation(self.atoms)

    def set_layers(self):
        pos = self.atoms.positions
        cell = self.atoms.cell
        x = cell[0]
        y = cell[1]
        z = np.array([0, 0, 0.8])

        self.x = x
        self.y = y
        self.z = z

        def frac(pos, cell=cell):
            return np.linalg.solve(cell, pos)

        self.pt.add_layer(Layer(name=DEFAULT_LAYER, color='#ffffff'))

        sites = {}
        sites['bridge1'] = {'pos': frac(.5 * (pos[2] + pos[1] - y) + z),
                            'tags': "strongbridge CO"}
        sites['bridge2'] = {'pos': frac(.5 * (pos[0] + pos[3]) + z),
                            'tags': "strongbridge CO"}
        sites['bridge3'] = {'pos': frac(.5 * (pos[0] + pos[2]) + z),
                            'tags': "weakbridge CO"}
        sites['bridge4'] = {'pos': frac(.5 * (pos[2] + pos[3] - x) + z),
                            'tags': "weakbridge CO"}
        sites['bridge5'] = {'pos': frac(.5 * (pos[3] + pos[1] + x) + z),
                            'tags': "weakbridge CO"}
        sites['bridge6'] = {'pos': frac(.5 * (pos[0] + pos[1]) + z),
                            'tags': "weakbridge CO"}

        sites['side1'] = {'pos': frac((pos[2] + pos[0] - y) / 2. + z),
                          'tags': "corner oxygen"}
        sites['side2'] = {'pos': frac((pos[2] + pos[3]) / 2. + z),
                          'tags': "corner oxygen"}
        sites['side3'] = {'pos': frac((pos[3] + pos[1] - y + x) / 2. + z),
                          'tags': "corner oxygen"}
        sites['side4'] = {'pos': frac((pos[0] + pos[1] + x) / 2. + z),
                          'tags': "corner oxygen"}

        sites['hollow1'] = {'pos': frac((pos[0] + pos[2] + pos[1] + pos[3] - x) /
                                    4. + z),
                            'tags': "hollow oxygen"}

        for name, data in sites.iteritems():
            tags = data['tags']
            site = Site(name=name,
                        default_species='empty',
                        layer=DEFAULT_LAYER,
                        tags=tags,
                        pos=data['pos'])
            self.pt.get_layers()[0].sites.append(site)
        # Create 'enlarged' coord set
        self.coord_set = self.pt.layer_list.generate_coord_set(size=[3, 3, 1],
                                                               layer_name=DEFAULT_LAYER)

    def set_species(self):
        # Species
        self.pt.add_species(Species(name='empty',
                       color='#ffffff',
                       representation=''))
        self.pt.add_species(Species(name='CO',
                       color='#000000',
                       representation='Atoms(\'CO\', [[0,0,0],[0,0,1.2]])'))
        self.pt.add_species(Species(name='O',
                       color='#ff0000',
                       representation='Atoms(\'O\')'))
        self.pt.species_list.default_species = 'empty'

    def set_parameters(self):
        self.pt.add_parameter(Parameter(name='T', value='600',
                                        adjustable=True,
                                        min='300',
                                        max='1500'))
        self.pt.add_parameter(Parameter(name='p_COgas', value='1.0',
                                        adjustable=True,
                                        scale='log',
                                        min=1.e-13,
                                        max=1.e2))
        self.pt.add_parameter(Parameter(name='p_O2gas', value='1.0',
                                        adjustable=True,
                                        scale='log',
                                        min=1.e-13,
                                        max=1.e2))
        self.pt.add_parameter(Parameter(name='A', value='(3.94*angstrom)**2'))


        self.pt.add_parameter(Parameter(name='E_CO_diff', value='0.4'))
        self.pt.add_parameter(Parameter(name='E_O_diff', value='0.5'))
        self.pt.add_parameter(Parameter(name='E_O_corner', value='-1.37'))
        self.pt.add_parameter(Parameter(name='E_O_hollow', value='-1.28'))
        self.pt.add_parameter(Parameter(name='E_CO_weak', value='-2.02'))
        self.pt.add_parameter(Parameter(name='E_CO_strong', value='-2.10'))
        self.pt.add_parameter(Parameter(name='E_react', value='0.9'))

    def set_processes(self):
        self.set_co_adsorption_desorption()
        self.set_co_diffusion()
        self.set_o2_adsorption_desorption()
        self.set_o_diffusion()
        self.set_reaction()

    def set_co_adsorption_desorption(self):
        # CO Adsorption/Desorption
        for i, coord in enumerate([x for x in self.coord_set if 'CO' in x.tags.split() and
                                                           not any(x.offset)]):
                blocked_coords = []
                for blocked_coord in self.coord_set:
                    if 0 < np.linalg.norm(coord.pos - blocked_coord.pos) < 3:
                        blocked_coords.append(blocked_coord)

                condition_list = [ConditionAction(coord=coord, species='empty')]
                for blocked_coord in blocked_coords:
                    condition_list.append(ConditionAction(coord=blocked_coord,
                                                          species='empty'))
                action_list = [ConditionAction(coord=coord, species='CO')]
                proc = Process(name='CO_adsorption_%02i' % i,
                              condition_list=condition_list,
                              action_list=action_list,
                              rate_constant='p_COgas*bar*A/2/sqrt(2*pi*umass*m_CO/beta)')

                self.pt.add_process(proc)

                # desorption
                if 'weak' in coord.tags:
                    rate_constant = 'p_COgas*bar*A/2/sqrt(2*pi*umass*m_CO/beta)*exp(beta*(E_CO_weak-mu_COgas)*eV)'
                elif 'strong' in coord.tags:
                    rate_constant = 'p_COgas*bar*A/2/sqrt(2*pi*umass*m_CO/beta)*exp(beta*(E_CO_strong-mu_COgas)*eV)'
                else:
                    raise UserWarning('Could not determine CO adsorption site type')

                condition_list = [ConditionAction(coord=coord, species='CO')]
                action_list = [ConditionAction(coord=coord, species='empty')]
                proc = Process(name='CO_desorption_%02i' % i,
                              condition_list=condition_list,
                              action_list=action_list,
                              rate_constant=rate_constant)
                self.pt.add_process(proc)


    def set_co_diffusion(self):
        # CO diffusion
        procs = 0
        for initial_coord in self.coord_set:
            if not any(initial_coord.offset) and 'CO' in initial_coord.tags:
                for final_coord in self.coord_set:
                    if 'CO' in final_coord.tags \
                      and 0 < np.linalg.norm(final_coord.pos - initial_coord.pos) < 2.9:

                        final_blocked_sites = [x for x in self.coord_set
                            if 0 < np.linalg.norm(x.pos-final_coord.pos) < 2.9 and \
                               0 < np.linalg.norm(initial_coord.pos-x.pos)
                                              ]

                        conditions = [ConditionAction(coord=initial_coord, species='CO'),
                                      ConditionAction(coord=final_coord, species='empty')]
                        conditions += [ ConditionAction(coord=blocked_site, species='empty')
                                        for blocked_site in final_blocked_sites ]

                        actions = [ConditionAction(coord=initial_coord, species='empty'),
                                   ConditionAction(coord=final_coord, species='CO')]

                        if 'weak' in final_coord.tags:
                            E_final = 'E_CO_weak'
                        elif 'strong' in final_coord.tags:
                            E_final = 'E_CO_strong'
                        else:
                            raise UserWarning

                        if 'weak' in initial_coord.tags:
                            E_initial = 'E_CO_weak'
                        elif 'strong' in initial_coord.tags:
                            E_initial = 'E_CO_strong'
                        else:
                            raise UserWarning

                        rate_constant = '1/(beta*h)*exp(-beta*(E_CO_diff+max(0,%s-%s))*eV)' % (
                                                                    E_final,
                                                                    E_initial)

                        self.pt.add_process(Process(name='CO_diffusion_%02i' % procs,
                                               condition_list=conditions,
                                               action_list=actions,
                                               rate_constant=rate_constant))
                        procs += 1

    def set_o2_adsorption_desorption(self):
        O2_pairs = [['side2','side4.(0,-1)'],
                    ['side1','side3'],
                    ['side4','side3'],
                    ['side2','hollow1.(1,0)'],
                    ['side1','hollow1'],
                    ['side3.(-1,0)', 'side2'],
                    ['hollow1', 'side4'],
                    ['side1', 'side2.(0,-1)'],
                    ['side4.(0,-1)', 'side1.(1,0)'],
                    ['side3', 'hollow1.(1, -1)']]


        for i, (a, b) in enumerate(O2_pairs):
            coord_a = self.pt.layer_list.generate_coord(a)
            coord_b = self.pt.layer_list.generate_coord(b)

            # O2 adsorption
            condition_list = [ConditionAction(coord=coord_a, species='empty'),
                              ConditionAction(coord=coord_b, species='empty')]
            action_list = [ConditionAction(coord=coord_a, species='O'),
                              ConditionAction(coord=coord_b, species='O')]

            condition_list += [ConditionAction(coord=blocked_site, species='empty')
                    for blocked_site in [blocked_site
                                for blocked_site in self.coord_set
                                if 0 < np.linalg.norm(coord_a.pos-blocked_site.pos) < 3 \
                                or 0 < np.linalg.norm(coord_b.pos-blocked_site.pos) < 3
                                        ]
                              ]

            rate_constant = 'p_O2gas*bar*A*2/sqrt(2*pi*umass*m_O2/beta)'

            self.pt.add_process(Process(name='O2_adsorption_%02i' % i,
                           condition_list=condition_list,
                           action_list=action_list,
                           rate_constant=rate_constant))


            # O2 desorption
            condition_list = [ConditionAction(coord=coord_a, species='O'),
                              ConditionAction(coord=coord_b, species='O')]
            action_list = [ConditionAction(coord=coord_a, species='empty'),
                              ConditionAction(coord=coord_b, species='empty')]

            if 'corner' in coord_a.tags:
                E_a = 'E_O_corner'
            elif 'hollow' in coord_a.tags:
                E_a = 'E_O_hollow'

            if 'corner' in coord_b.tags:
                E_b = 'E_O_corner'
            elif 'hollow' in coord_b.tags:
                E_b = 'E_O_hollow'

            rate_constant = 'p_O2gas*bar*A*2/sqrt(2*pi*umass*m_O2/beta)*' + \
                            'exp(beta*(%s+%s-mu_O2gas)*eV)' % (E_a, E_b)

            self.pt.add_process(Process(name='O2_desorption_%02i' % i,
                                   condition_list=condition_list,
                                   action_list=action_list,
                                   rate_constant=rate_constant))

    def set_o_diffusion(self):
        # O diffusion
        procs = 0
        for initial_coord in self.coord_set:
            if not any(initial_coord.offset) and 'oxygen' in initial_coord.tags:
                final_coords = []
                for final_coord in self.coord_set:
                    if 'oxygen' in final_coord.tags \
                      and 0 < np.linalg.norm(final_coord.pos - initial_coord.pos) < 3:
                        final_blocked_sites = []
                        for final_blocked in self.coord_set:
                            if 0 < np.linalg.norm(final_blocked.pos - final_coord.pos) < 2.9 \
                                and 0 < np.linalg.norm(initial_coord.pos-final_blocked.pos):
                                    final_blocked_sites.append(final_blocked)
                        conditions = []
                        conditions.append(ConditionAction(coord=initial_coord,
                                                          species='O'))
                        conditions.append(ConditionAction(coord=final_coord,
                                                          species='empty'))
                        for blocked_site in final_blocked_sites:
                            conditions.append(ConditionAction(coord=blocked_site,
                                                             species='empty'))
                        actions = [ConditionAction(coord=initial_coord, species='empty'),
                                   ConditionAction(coord=final_coord, species='O')]

                        if 'corner' in initial_coord.tags:
                            E_initial = 'E_O_corner'
                        elif 'hollow' in initial_coord.tags:
                            E_initial = 'E_O_hollow'

                        if 'corner' in final_coord.tags:
                            E_final = 'E_O_corner'
                        elif 'hollow' in final_coord.tags:
                            E_final = 'E_O_hollow'

                        rate_constant = '1/(beta*h)*exp(-beta*(E_O_diff+max(0,%s-%s))*eV)' % (E_final, E_initial)
                        self.pt.add_process(Process(name='O_diffusion_%02i' % procs,
                                               condition_list=conditions,
                                               action_list=actions,
                                               rate_constant=rate_constant))
                        procs += 1

    def set_reaction(self):
        # Reaction
        procs = []
        for O_coord in self.coord_set:
            if not any(O_coord.offset) and 'oxygen' in O_coord.tags:
                for CO_coord in self.coord_set:
                    if 'CO' in CO_coord.tags \
                      and 1.5 < np.linalg.norm(CO_coord.pos - O_coord.pos) < 4.3 :
                        condition_list = [ConditionAction(coord=O_coord, species='O'),
                                        ConditionAction(coord=CO_coord, species='CO')]

                        action_list = [ConditionAction(coord=O_coord, species='empty'),
                                       ConditionAction(coord=CO_coord, species='empty')]

                        proc = Process(name='Reaction_%02i' % len(procs),
                                       condition_list=condition_list,
                                       action_list=action_list,
                                       rate_constant='1/(beta*h)*exp(-beta*E_react*eV)',
                                       tof_count={'CO_oxidation':1})

                        procs.append(proc)

        for proc in procs:
            self.pt.add_process(proc)


def main():
    builder = ModelBuilder()
    builder.standard_build()
    builder.export('CO_oxidation_on_Pdsqrt5.xml')

    builder = ModelBuilder()
    builder.pd100_build()
    builder.export('CO_oxidation_on_Pd100.xml')

def test_man():
    cwd = os.curdir
    os.chdir(os.path.abspath(os.path.dirname(__file__)))
    main()
    os.chdir(cwd)

if __name__ == '__main__':
    main()
