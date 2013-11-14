Modeling lateral interaction
============================

Introduction
^^^^^^^^^^^^


Lateral Interaction Models
^^^^^^^^^^^^^^^^^^^^^^^^^^
- pairwise interaction
- bond-order potentials

Conquering combinatorics with itertools
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Even restricting oneself to nearest neighbor
lateral interaction to number of different
configurations to be considered for lateral
interactions can quickly reach a couple
of tens or hundred. A phenomenon which is
among practitioners humbly referred to as
*combinatorial explosions*. Unfortunately
manualy typing all these combinations if
usually tiring and thus error prone.
Fortunately the `itertools` module from the
python standard library allows to very quickly
generate all needed configurations. Before
delving into the practical steps of this I
would like to point out that lateral interaction
typically slows down the simulation by about
one order of magnitude, which is a purely
empirical fact.
