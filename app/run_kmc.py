#!/usr/bin/python
"""Generical kMC steering script for binary modules created kmos"""


from kmc import lattice, proclist

proclist.init((10,)*int(lattice.model_dimension),'foobar', lattice.default_layer, proclist.default_species)
print("Finished initialization")
for i in xrange(int(3.e6)):
    proclist.do_kmc_step()
