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
