kmos/lattice
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    Implements the mappings between the real space lattice
    and the 1-D lattice, which kmos/base operates on.
    Furthermore replicates all geometry specific functions of kmos/base
    in terms of lattice coordinates.
    Using this module each site can be addressed with 4-tuple
    ``(i, j, k, n)`` where ``i, j, k`` define the unit cell and
    ``n`` the site within the unit cell.

lattice/allocate_system
""""""""""""""""""""""""""""""""""""""""""""""""""
    Allocates system, fills mapping cache, and
    checks whether mapping is consistent

    ``none``

lattice/calculate_lattice2nr
""""""""""""""""""""""""""""""""""""""""""""""""""
    Maps all lattice coordinates onto a continuous
    set of integer :math:`\in [1,volume]`

    - ``site`` integer array of size (4) a lattice coordinate

lattice/calculate_nr2lattice
""""""""""""""""""""""""""""""""""""""""""""""""""
    Maps a continuous set of
    of integers :math:`\in [1,volume]` to a
    4-tuple representing a lattice coordinate

    - ``nr`` integer representing the site index

lattice/deallocate_system
""""""""""""""""""""""""""""""""""""""""""""""""""
    Deallocates system including mapping cache.

    ``none``

lattice/default_layer
""""""""""""""""""""""""""""""""""""""""""""""""""
   The layer in which the model is initially in by default (only relevant for multi-lattice models).

lattice/lattice2nr
""""""""""""""""""""""""""""""""""""""""""""""""""
   Caching array holding the mapping from index to lattice
   coordinate:  (x, y, z, n) -> i.

lattice/model_dimension
""""""""""""""""""""""""""""""""""""""""""""""""""
   Store the number of dimensions of this model: 1, 2, or 3

lattice/nr2lattice
""""""""""""""""""""""""""""""""""""""""""""""""""
   Caching array holding the mapping from index to lattice
   coordinate: i -> (x, y, z, n).

lattice/nr_of_layers
""""""""""""""""""""""""""""""""""""""""""""""""""
   Constant storing the number of layers (for multi-lattice models > 1)

lattice/site_positions
""""""""""""""""""""""""""""""""""""""""""""""""""
   The positions of (adsorption) site in the unit cell in
   fractional coordinates.

lattice/spuck
""""""""""""""""""""""""""""""""""""""""""""""""""
   spuck = Sites Per Unit Cell Konstant
   The number of sites per unit cell, i.e. for coordinate
   notation (x, y, n) this is the maximum value of `n`.

lattice/system_size
""""""""""""""""""""""""""""""""""""""""""""""""""
   Stores the current size of the allocated system lattice (x, y, z)
   in an integer array. In low-dimensional system, corresponding entries will be set to 1.
   Note that this should be thought of as a read-only variable. Changing its value at model
   runtime will not the indented effect of actually changing the simulated lattice.
   The definitive location for custom lattice size is `simulation_size` in `kmc_settings.py`.

   If the system size shall be changed programmatically, it needs to happen before the `KMC_Model`
   is instantiated and Fortran array are allocated accordingly, like to

       #!/usr/bin/env python

       import kmc_settings
       import kmos.run

       kmc_settings.simulation_size = 9, 9, 4

       with kmos.run.KMC_Model() as model:
           print(model.lattice.system_size)))`

lattice/unit_cell_size
""""""""""""""""""""""""""""""""""""""""""""""""""
   The dimensions of the unit cell (e.g. in Angstrom) of the
   unit cell.
