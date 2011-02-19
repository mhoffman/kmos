#!/usr/bin/ipython
"""Generical kMC steering script for binary modules created kmos"""


from copy import deepcopy
import numpy as np
import ase
from ase.atoms import Atom, Atoms
from kmc import base, lattice, proclist
import pickle

class KMC_Model():
    def __init__(self, size=10, system_name='kmc_model'):
        proclist.init((size,)*int(lattice.model_dimension),system_name, lattice.default_layer, proclist.default_species)
        self.cell_size = np.dot(lattice.unit_cell_size, lattice.system_size)
        self.species_representation = []
        # This clumsy loop is neccessary because f2py
        # can unfortunately only pass through one character
        # at a time and not strings
        for ispecies in range(len(proclist.species_representation)):
            repr = ''
            for jchar in range(proclist.representation_length):
                char = proclist.get_representation_char(ispecies+1, jchar+1)
                repr += char
            if repr.strip():
                self.species_representation.append(eval(repr))
            else:
                self.species_representation.append(None)



    def run_steps(self, n):
        for i in xrange(n):
            proclist.do_kmc_step()

    def get_atoms(self):
        initialized = False
        atoms = None
        for i in xrange(lattice.system_size[0]):
            for j in xrange(lattice.system_size[1]):
                for k in xrange(lattice.system_size[2]):
                    for n in xrange(1,1+lattice.spuck):
                        species = lattice.get_species([i,j,k,n]) - 1
                        if self.species_representation[species]:
                            atom = deepcopy(self.species_representation[species])
                            atom.translate(np.dot(lattice.unit_cell_size,
                            np.array([i,j,k]) + lattice.site_positions[n-1]))
                            if initialized:
                                atoms += atom
                            else:
                                atoms = atom
                                initialized = True
        if atoms:
            atoms.set_cell(self.cell_size)
        return atoms
                    
                    
                

        
if __name__ == '__main__':
    model  = KMC_Model()
