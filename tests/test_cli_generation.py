#!/usr/bin/env python

import os


def generate_model():
    import kmos
    from kmos.gui import KMC_Editor
    from kmos.types import *

    editor = KMC_Editor()
    project = editor.project_tree
    # set meta information
    model_name = 'test_cli_generated_model'
    project.meta.author = 'Max J. Hoffmann'
    project.meta.email = 'mjhoffmann@gmail.com'
    project.meta.model_dimension = '2'
    project.meta.debug = 0
    project.meta.model_name = model_name

    # add layer
    project.add_layer(Layer(name='default', sites=[
        Site(name='cus', x=0, y=0.5, z=0.5)]))

    # add species
    project.add_species(Species(name='oxygen', color='#ff0000'))
    project.add_species(Species(name='CO', color='#000000'))
    project.add_species(Species(name='empty', color='#ffffff'))
    project.species_list_iter.default_species = 'empty'

    # add parameters
    project.add_parameter(Parameter(name='p_CO', value=0.2, scale='log'))
    project.add_parameter(Parameter(name='T', value=500, adjustable=True))
    project.add_parameter(Parameter(name='p_O2', value=1.0, adjustable=True))

    # add processes
    cus = Coord(name='cus', layer='default')
    p = Process(name='CO_adsorption', rate_constant='1000.')
    p.add_condition(ConditionAction(species='empty', coord=cus))
    p.add_action(ConditionAction(species='CO', coord=cus))
    project.add_process(p)

    p = Process(name='CO_desorption', rate_constant='1000.')
    p.add_condition(ConditionAction(species='CO', coord=cus))
    p.add_action(ConditionAction(species='empty', coord=cus))
    project.add_process(p)
    return project


def test_model_generation_and_export():
    from kmos.export import export_source
    model = generate_model()
    cwd = os.path.abspath(os.curdir)
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    assert export_source(model)
    os.chdir(cwd)

if __name__ == '__main__':
    test_model_generation_and_export()
