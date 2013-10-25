#!/usr/bin/env python
"""
    Just a small cursory script how multi-dentate adsorption geometry
    can be implemented. The rules and rates contain no physical input
    and diffusion and rotation is also missing. But it would be
    straightforward to extend.

"""

from kmos.types import *


pt = Project()

pt.add_species(name='empty')
pt.add_species(name='CC_up', representation="Atoms('CC', [[0,0,0], [0,2,0]])")
pt.add_species(name='CC_up_1', representation="")

pt.add_species(name='CC_right', representation="Atoms('NN', [[0,0,0], [2,0,0]])")
pt.add_species(name='CC_right_1', representation="")
layer = pt.add_layer(name='simple_cubic')
layer.sites.append(Site(name='hollow', pos='0.5 0.5 0.5',
                        default_species='empty'))

pt.lattice.cell = np.diag([3.5, 3.5, 10])

pt.set_meta(author = 'Your Name',
            email = 'your.name@server.com',
            model_name = 'MyFirstModel',
            model_dimension = 2,)
pt.add_parameter(name='A', value='(3.5*angstrom)**2')

pt.add_parameter(name='adsorption_up', adjustable=True, min=1, max=1000, value=500)
pt.add_parameter(name='desorption_up', adjustable=True, min=1, max=1000, value=500)

pt.add_parameter(name='adsorption_right', adjustable=True, min=1, max=1000, value=500)
pt.add_parameter(name='desorption_right', adjustable=True, min=1, max=1000, value=500)

coord = pt.lattice.generate_coord

pt.add_process(name="CC_adsorption_up",
               conditions=[Condition(species='empty', coord=coord('hollow')),
                           Condition(species='empty', coord=coord('hollow.(0,1,0)')),
                          ],
               actions=[Action(species='CC_up', coord=coord('hollow')),
                        Action(species='CC_up_1', coord=coord('hollow.(0,1,0)'))
                       ],
               rate_constant='adsorption_up')

pt.add_process(name="CC_desorption_up",
               conditions=[Condition(species='CC_up', coord=coord('hollow')),
                          Condition(species='CC_up_1', coord=coord('hollow.(0,1,0)')),],
               actions=[Action(species='empty', coord=coord('hollow')),
                        Action(species='empty', coord=coord('hollow.(0,1,0)')),
                       ],
               rate_constant='desorption_up')

pt.add_process(name="CC_adsorption_right",
               conditions=[Condition(species='empty', coord=coord('hollow')),
                           Condition(species='empty', coord=coord('hollow.(1,0,0)')),
                          ],
               actions=[Action(species='CC_right', coord=coord('hollow')),
                       Action(species='CC_right_1', coord=coord('hollow.(1,0,0)')),],
               rate_constant='adsorption_right')

pt.add_process(name="CC_desorption_right",
               conditions=[Condition(species='CC_right', coord=coord('hollow')),
                          Condition(species='CC_right_1', coord=coord('hollow.(1,0,0)')),],

               actions=[Action(species='empty', coord=coord('hollow')), Action(species='empty', coord=coord('hollow.(1,0,0)')) ],
               rate_constant='desorption_right')

pt.filename =  'multidentate.xml'
pt.save()
