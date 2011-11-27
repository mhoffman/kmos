#!/usr/bin/env python

import tempfile
import sys
import os
import shutil

from kmos.types import *
from kmos.io import *

pt = Project()
outdir = tempfile.mkdtemp()
outdir = 'outdir'
outdir
pt.meta.model_dimension = 2
pt.species_list.default_species = 'default'

pt.meta.model_name = 'example'
pt.meta.model_name = 'some_model'
pt.meta.author = 'some guy'
pt.meta.email = 'some.guy@server.org'

pt.add_layer(name='default')
pt.get_layers()[0].add_site(Site(name='default'))
pt.add_species(name='a',representation='')
pt.add_species(name='b',representation='')

pt.species_list.default_species = 'a'
coord = pt.layer_list.generate_coord('default.(0,0,0).default')

pt.add_process(name='ab',
               condition_list=[Condition(coord=coord, species='a')],
               action_list=[Condition(coord=coord, species='b')],
               )
pt.add_process(name='ba',
               condition_list=[Condition(coord=coord, species='b')],
               action_list=[Condition(coord=coord, species='a')],
               )
export_source(pt, outdir)

shutil.rmtree(outdir)
