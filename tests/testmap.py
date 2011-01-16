#!/usr/bin/python

import sys
sys.path.append('../fortran_src')
import run_kmc, kmc

r = run_kmc.KMC_Run()
for lattice in r.lattice_names:
    nr2lattice =  eval('kmc.lattice.nr2%s' % lattice)
    lattice2nr =  eval('kmc.lattice.%s2nr' % lattice)
    for i in xrange(1,1+kmc.base.get_volume()):
        site = nr2lattice(i)
        j = lattice2nr(site)
        print(i,site,j)
        if i != j :
            print("WRONG")
            break
    else:
        print("OLL KLEAR")
        
