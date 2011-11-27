kmos/proclist
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    Implements the kMC process list.

proclist/do_kmc_step
""""""""""""""""""""""""""""""""""""""""""""""""""
    Performs exactly one kMC step.

    ``none``

proclist/get_occupation
""""""""""""""""""""""""""""""""""""""""""""""""""
    Evaluate current lattice configuration and returns
    the normalized occupation as matrix. Different species
    run along the first axis and different sites run
    along the second.

    ``none``

proclist/init
""""""""""""""""""""""""""""""""""""""""""""""""""
     Allocates the system and initializes all sites in the given
     layer.

    * ``input_system_size`` number of unit cell per axis.
    * ``system_name`` identifier for reload file.
    * ``layer`` initial layer.
    * ``no_banner`` [optional] if True no copyright is issued.

proclist/initialize_state
""""""""""""""""""""""""""""""""""""""""""""""""""
    Initialize all sites and book-keeping array
    for the given layer.

    * ``layer`` integer representing layer

proclist/run_proc_nr
""""""""""""""""""""""""""""""""""""""""""""""""""
    Runs process ``proc`` on site ``nr_site``.

    * ``proc`` integer representing the process number
    * ``nr_site``  integer representing the site
