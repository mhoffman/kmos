#!/usr/bin/env python

import tempfile
import sys
import os
import shutil

from kmos.types import *
from kmos.io import *

# Copy DTD
import kmos
shutil.copy(os.path.join(os.path.dirname(kmos.__file__),
                                'kmc_project_v0.2.dtd'),
            '.')



# Fetch doc from dummy project

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
pt.add_species(name='a', representation='')
pt.add_species(name='b', representation='')

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

for prefix in ['base', 'lattice', 'proclist']:
    os.system('robodoc --src %s.f90 --doc %s --singlefile --ascii'
               % (os.path.join(outdir, prefix), prefix))

    asci = file('%s.txt' % prefix, 'r').readlines()


    new_asci = []
    jump = 0
    for i, line in enumerate(asci):
        if jump:
            jump += -1
            continue
        if not i:
        # make first line header
            new_asci.append(line)
            new_asci.append('^' * 40 + '\n')
        elif i >= len(asci) - 2:
        # ignore last line
            continue
        elif 'FUNCTION' in line:
        # ignore the function string
            continue
        elif 'ARGUMENTS' in line:
        # ignore the arguments string
            new_asci.append('\n')
        elif '------' in line:
            new_asci.append(asci[i + 1])
            new_asci.append('"' * 50)
            jump = 1
        else:
            new_asci.append(line)
    rst = file('%s.rst' % prefix, 'w')
    for line in new_asci:
        rst.write(line)
    rst.close()

    os.system('rm %s.txt' % prefix)
    #os.system('rst2html base.rst > base.html')

shutil.rmtree(outdir)
