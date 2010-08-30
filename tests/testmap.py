#!/usr/bin/python

import run_kmc, kmc

r = run_kmc.KMC_Run()
for i in range(1,1+kmc.base.get_volume()):
    site = kmc.lattice.nr2ruo2(i)
    j = kmc.lattice.ruo22nr(site)
    print(i,site,j)
    if i != j :
        print("WRONG")
        break
else:
    print("OLL KLEAR")
        
