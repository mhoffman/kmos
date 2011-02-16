#!/usr/bin/python
"""Generical kMC steering script for binary modules created kmos"""


from kmc import lattice, proclist

proclist.init((10,10),'foobar', lattice.ruo2, proclist.empty)
print("Finished initialization")
