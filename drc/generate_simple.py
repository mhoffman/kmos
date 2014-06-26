#!/usr/bin/env python

#DISCLAIMER: this is hacked down really quickly
#BEWARE OF BUGS

from kmos.types import *
from kmos.io import *
import numpy as np

pt = Project()


pt.set_meta(author='Felix Engelmann',
            email='felix.engelmann@tum.de',
            model_dimension=1,
            model_name='simple_model')
pt.add_species(name='empty')
pt.add_species(name='A')
pt.add_species(name='B')

pt.add_layer(name='default')
pt.add_site(layer='default',
            pos='0 0 0',
            name='s')

coord = pt.layer_list.generate_coord

pt.add_process(name='adsA',
               rate_constant='1000',
               conditions=[Condition(species='empty', coord=coord('s'))],
               actions=[Action(species='A', coord=coord('s'))])
			   
pt.add_process(name='adsB',
               rate_constant='50',
               conditions=[Condition(species='empty', coord=coord('s'))],
               actions=[Action(species='B', coord=coord('s'))])

pt.add_process(name='desA',
               rate_constant='80',
               conditions=[Condition(species='A', coord=coord('s'))],
               actions=[Action(species='empty', coord=coord('s'))])
			   
pt.add_process(name='desB',
               rate_constant='700',
               conditions=[Condition(species='B', coord=coord('s'))],
               actions=[Action(species='empty', coord=coord('s'))])

pt.add_process(name='react',
               rate_constant='200',
               conditions=[Condition(species='A', coord=coord('s'))],
               actions=[Action(species='B', coord=coord('s'))],
               tof_count={'react': 1})
			   
pt.add_process(name='unreact',
               rate_constant='30',
               conditions=[Condition(species='B', coord=coord('s'))],
               actions=[Action(species='A', coord=coord('s'))],
               tof_count={'unreact': 1})

pt.filename = 'simple.xml'
pt.save()
