#!/bin/bash -eu

gfortran -c kind_values_f2py.f90 -g -pg
gfortran -c base.f90 -cpp -g -pg
gfortran -c lattice.f90 -g -pg
gfortran -c proclist.f90 -g -pg
gfortran -o run_kmc run_kmc.f90 kind_values_f2py.o base.o lattice.o proclist.o -g -pg
