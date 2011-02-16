#!/usr/bin/python
"""Generical kMC steering script for binary modules created kmos"""


from kmc import lattice, proclist

proclist.init((10,10),'foobar', lattice.default_layer, proclist.default_species)
print("Finished initialization")
for i in xrange(1000000):
    proclist.do_kmc_step()
