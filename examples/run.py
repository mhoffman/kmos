#!/usr/bin/env python
"""Very simple run script for evaluating a KMC_Model.

This script should be run from a directory where
a compiled model (having kmc_settings.py/kmc_model.[so|pyd])
resides.

The attribute names (p_O2gas, T, p_COgas) of ScanKinetics
have to be defined in the your model.
The final configuration of each kMC run
will be stored in a subdirectory ScanKinetics_configs
for caching, the output data will be stored in ScanKinetics.dat.

To allow execution from multiple hosts connected
to the same filesystem calculated points are blocked
via ScanKinetics.lock. To redo a calculation ScanKinetics.dat
and ScanKinetics.lock should be moved out of the way.
"""

from kmos.run import ModelRunner, PressureParameter, TemperatureParameter


class ScanKinetics(ModelRunner):
    p_O2gas = PressureParameter(1)
    T = TemperatureParameter(600)
    p_COgas = PressureParameter(min=1, max=10, steps=40)


ScanKinetics().run(init_steps=1e7, sample_steps=1e7, cores=4)
