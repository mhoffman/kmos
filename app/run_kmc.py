#!/usr/bin/ipython
"""Generical kMC steering script for binary modules created kmos"""


import numpy as np
import ase
from kmc import base, lattice, proclist

class KMC_Model():
    def __init__(self, size=10, system_name='kmc_model'):
        proclist.init((size,)*int(lattice.model_dimension),system_name, lattice.default_layer, proclist.default_species)
        self.cell_size = np.dot(lattice.unit_cell_size, lattice.system_size)

    def __del__(self):
        base.deallocate_system()
            

    def run_steps(self, n):
        for i in xrange(n):
            proclist.do_kmc_step()

        
if __name__ == '__main__':
    model  = KMC_Model()
