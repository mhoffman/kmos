#!/usr/bin/python

import sys
sys.path.append('../fortran_src')
import run_kmc, kmc

r = run_kmc.KMC_Run()
for lattice in r.lattice_names:
    for i in range(1,1+kmc.base.get_volume()):
        site = eval('kmc.lattice.nr2%s(i)' % lattice)
        j = eval('kmc.lattice.%s2nr(site)' % lattice)
        print(i,site,j)
        if i != j :
            print("WRONG")
            break
    else:
        print("OLL KLEAR")
        
