================
Trouble Shooting
================

What other kMC codes are there?
  Kinetic Monte Carlo codes that I am currently aware of,
  that are in some form released on the intertubes are
  with no claim of completeness :

  - `akmc <http://theory.cm.utexas.edu/vtsttools/akmc/>`_ (G. Henkelman)
  - `Carlos <http://www.win.tue.nl/~johanl/projects/Carlos/>`_ (J. Lukkien)
  - `chimp <http://www.koders.com/cpp/fid7FA324E3E76DB9874158BE3CF722405FA44AECE8.aspx?s=mdef%3Ainsert>`_ (D. Dooling)
  - `mapkmc <http://www.dion.che.udel.edu/downloads.php>`_ (D. Vlachos)
  - `Monty <http://www.vsc.science.ru.nl/deij/monty.html>`_ (SXM Boerrrigter)
  - `MoCKa <http://www.itcp.kit.edu/deutschmann/288.php>`_ (L. Kunz)
  - `NASCAM <http://www.fundp.ac.be/sciences/physique/larn/NASCAM-Homepage>`_ (S. Lucas)
  - `Spparks <http://www.cs.sandia.gov/~sjplimp/spparks/doc/Manual.html>`_ (S. Plimpton):

  Though The Google might find you some more.
  Please drop me a line if you find any information
  inaccurate.

What does kmos stand for anyways?
  Good question, initially kmos was supposed to stand for
  `kinetic modeling on steroids`, but that confused people
  too much since we are not modelling steroids but surfaces.
  Some popular variants are

    - kMC modeling of surfaces
    - kmos modeling offering source

  I am open for other suggestions.


When I use `kmos shell` the model doesn't have the species and sites
I have defined.
    Note that Fortran is case-insensitive. Therefore f2py turns
    all variable and functions names into lower case by convention.
    Try to lower-case your species or site name.

When I run kmos the GUI way and close it, it seems to hang and I need to use the window manager to kill it.
  This is a bug waiting to be fixed. To avoid it close
  the window showing the atoms object by clicking on its
  close button or Alt-F4 or whichever shortcut your WM uses.

Running a model it sometimes prints
`Warning: numerical precision too low, to resolve time-steps`
  This means that the kMC step of the current process was so
  small compared to the current kMC time that for the processor
  :math:`t + \Delta t = t`. This should under normal circumstances
  only occur if you changed external conditions during a kMC run.

  Otherwise it could mean that your rate constants vary over
  12 or more orders of magnitude. If this is the case one needs
  to wonder whether non-coarse graind kMC is actually the right
  approach for the system. On the hand because the selection of
  the next process will no longer be reliable and second because
  reasonable sampling of all involved process may no longer happen.


When running a model without GUI evaluation steps seem very slow.
  If you have a `kmos.run.KMC_Model` instance and call `model.get_atoms()`
  the generation of the real-space geometry takes the longest time. If you
  only have to evaluate coverages or turn-over frequencies you are
  better off using `model.get_atoms(geometry=False)`, which returns an
  object with all numbers but without the actual geometry.

What units is kmos using ?
  By default length are measured in angstrom, energies in eV, pressure
  in bar, constants are taken from CODATA 2010. Note that the rate
  expressions though contain explicit conversion factors like `bar`,
  `eV` etc. If in doubt check the resulting rate constants by hand.

When running the model I sometimes get mysterious `infty` or `nan` values!
  This most likely can be traced back to fact that some variable ran outside
  its range and is caused by the fact that the wrong `kind` values are chosen
  (Fortran stuff). Kind values are currently all hard-code in the the `src`
  directory at `/path-to-export/src/kind_values_f2py.f90` and set for ifort.
  While I am working to have this set dynamically at compile time, you have
  to figure out the right `kind` value for your compiler for now.

How can I change the occupation of a model at runtime?
  This is explained in detail at :ref:`manipulate_model_runtime` though
  the import bit is that you call ::

     model._adjust_database()

  after changing the occupation and before doing the next kMC step.


How can I quickly obtain k_tot ?
    That is ::
        model.base.get_accum_rate(model.proclist.nr_of_proc)

How can I check the system size ?
    You can check ::
        model.lattice.system_size
    to get the number of unit cell in the x, y, and z direction.
    The number of sites per unit cell is stored in ::
        model.lattice.spuck
    a.k.a Sites Per Unit Cell Konstant :-).
    Or you check ::
        model.base.get_volume()
    to get the total number of sites, i.e. ::
        model.base.get_volume() == model.lattice.system_size.prod()*model.lattice.spuck
        => True


More to follow.

Please post issues
`here <https://github.com/mhoffman/kmos/issues>`_
or via email mjhoffmann .at. gmail .dot. com
or via twitter @maxjhoffmann

.. TODO:: Explain `post-mortem` procedure
