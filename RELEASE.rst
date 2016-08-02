=============
RELEASE NOTES
=============

develop
=======

0.3.21
=======

Doc improvements

0.3.20
======

Auto-correlation function (acf) and root-mean-square displacement
features contributed by Andreas Garhammer. Documentation to
follow. Technical demo in <PROJECT_ROOT>/tests/test_acf/test_run_acf.py
TODO: ACF & RMSD Documentation

0.3.19
=======

Added .github/ contributor information

0.3.18
======

Fixed bug in get_std_sampled_data not resetting sampling,
discussed `here <https://github.com/mhoffman/kmos/pull/51>`_

0.3.17
=======

Break out lxml as hard dependency
New input file format for models (akin to .ini format)
Introduced new templating format to make kmos/io.py cleaner.
Merged 'otf' backend from JM Lorenzi for highly flexible rate-constants expressions (still somewhat experimental)

0.3.10-0.3.16
=============

Bugfixes

0.3.7-0.3.9
===========

Bugfix releases for non-orthogonal 3D lattices.

0.3.6
=====

Released in reference paper Hoffmann, Max J., Sebastian Matera, and Karsten Reuter. "kmos: A lattice kinetic Monte Carlo framework." Computer Physics Communications 185.7 (2014): 2138-2150.
