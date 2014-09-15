kmos/base
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

    The base kMC module, which implements the kMC method on a :math:`d = 1`
    lattice. Virtually any lattice kMC model can be build on top of this.
    The methods offered are:

    * de/allocation of memory
    * book-keeping of the lattice configuration and all available processes
    * updating and tracking kMC time, kMC step and wall time
    * saving and reloading the current state
    * determine the process and site to be executed

base/accum_rates
""""""""""""""""""""""""""""""""""""""""""""""""""
   Stores the accumulated rate constant multiplied with the number
   of sites available for that process to be used by determine_procsite.
   Let :math:`\mathbf{c}` be the rate constants :math:`\mathbf{n}`
   the number of available sites, and :math:`\mathbf{a}`
   the accumulated rates, then :math:`a_{i}`
   is calculated according to :math:`a_{i}=\sum_{j=1}^{i} c_{j} n_{j}`.

base/add_proc
""""""""""""""""""""""""""""""""""""""""""""""""""
    The main idea of this subroutine is described in del_proc. Adding one
    process to one capability is programmatically simpler since we can just
    add it to the end of the respective array in avail_sites.

    * ``proc`` positive integer number that represents the process to be added.
    * ``site`` positive integer number that represents the site to be manipulated

base/allocate_system
""""""""""""""""""""""""""""""""""""""""""""""""""
   Allocates all book-keeping structures and stores
   local copies of system name and size(s):

   * ``systen_name`` identifier of this simulation, used as name of punch file
   * ``volume`` the total number of sites
   * ``nr_of_proc`` the total number of processes

base/assertion_fail
""""""""""""""""""""""""""""""""""""""""""""""""""
    Function that shall be used by all parts of the program to print a
    proper message in case some assertion fails.

    * ``a`` condition that is supposed to hold true
    * ``r`` message that is printed to the poor user in case it fails

base/avail_sites
""""""""""""""""""""""""""""""""""""""""""""""""""
   Main book-keeping array that stores for each process the sites
   that are available and for each site the address
   in this very array. The meaning of the fields are:

       avail_sites(proc, field, switch)

   where:

   * proc -- refers to a process in the process list
   * the field within the process, but the meaning differs as explained
     under 'switch'
   * switch -- can be either 1 or 2 and switches between
     (1) the actual numbers of the sites, which are available
     and filled in from the left but in whatever order they come
     or (2) the location where the site is stored in (1).

base/can_do
""""""""""""""""""""""""""""""""""""""""""""""""""
    Returns true if 'site' can do 'proc' right now

    * ``proc`` integer representing the requested process.
    * ``site`` integer representing the requested site.
    * ``can`` writeable boolean, where the result will be stored.

base/deallocate_system
""""""""""""""""""""""""""""""""""""""""""""""""""
    Deallocate all allocatable arrays: avail_sites, lattice, rates,
    accum_rates, integ_rates, procstat.

    ``none``

base/del_proc
""""""""""""""""""""""""""""""""""""""""""""""""""
    del_proc delete one process from the main book-keeping array
    avail_sites. These book-keeping operations happen in O(1) time with the
    help of some more book-keeping overhead. avail_sites stores for each
    process all sites that are available. The array for each process is
    filled from the left, but sites generally not ordered. With this
    determine_procsite can effectively pick the next site and process. On
    the other hand a second array (avail_sites(:,:,2) ) holds for each
    process and each site, the location where it is stored in
    avail_site(:,:,1). If a site needs to be removed this subroutine first
    looks up the location via avail_sites(:,:,1) and replaces it with the
    site that is stored as the last element for this process.

    * ``proc`` positive integer that states the process
    * ``site`` positive integer that encodes the site to be manipulated

base/determine_procsite
""""""""""""""""""""""""""""""""""""""""""""""""""
    Expects two random numbers between 0 and 1 and determines the
    corresponding process and site from accum_rates and avail_sites.
    Technically one random number would be sufficient but to circumvent
    issues with wrong interval_search_real implementation or rounding
    errors I decided to take two random numbers:

    * ``ran_proc`` Random real number from :math:`\in[0,1]` that selects the next process
    * ``ran_site`` Random real number from :math:`\in[0,1]` that selects the next site
    * ``proc`` Return integer :math:`\in[1,\mathrm{nr\_of\_proc}`
    * ``site`` Return integer :math:`\in [1,\mathrm{volume}`

base/get_accum_rate
""""""""""""""""""""""""""""""""""""""""""""""""""
    Return accumulated rate at a given process.

    * ``proc_nr`` integer representing the requested process.
    * ``return_accum_rate`` writeable real, where the requested accumulated rate will be stored.

base/get_avail_site
""""""""""""""""""""""""""""""""""""""""""""""""""
    Return field from the avail_sites database

    * ``proc_nr`` integer representing the requested process.
    * ``field`` integer for the site at question
    * ``switch`` 1 or 2 for site or storage location

base/get_integ_rate
""""""""""""""""""""""""""""""""""""""""""""""""""
    Return integrated rate at a given process.

    * ``proc_nr`` integer representing the requested process.
    * ``return_integ_rate`` writeable real, where the requested integrated rate will be stored.

base/get_kmc_step
""""""""""""""""""""""""""""""""""""""""""""""""""
    Return the current kmc_step

    * ``kmc_step`` Writeable integer

base/get_kmc_time
""""""""""""""""""""""""""""""""""""""""""""""""""
    Returns current kmc_time as rdouble real as defined in kind_values.f90.

    * ``return_kmc_time`` writeable real, where the kmc_time will be stored.

base/get_kmc_time_step
""""""""""""""""""""""""""""""""""""""""""""""""""
    Returns current kmc_time_step (the time increment).

    * ``return_kmc_step`` writeable real, where the kmc_time_step will be stored.

base/get_kmc_volume
""""""""""""""""""""""""""""""""""""""""""""""""""
    Return the total number of sites.

    * ``volume`` Writeable integer.

base/get_nrofsites
""""""""""""""""""""""""""""""""""""""""""""""""""
    Return how many sites are available for a certain process.
    Usually used for debugging

    * ``proc`` integer  representing the requested process
    * ``return_nrofsites`` writeable integer, where nr of sites gets stored

base/get_procstat
""""""""""""""""""""""""""""""""""""""""""""""""""
    Return process counter for process proc as integer.

    * ``proc`` integer representing the requested process.
    * ``return_procstat`` writeable integer, where the process counter will be stored.

base/get_rate
""""""""""""""""""""""""""""""""""""""""""""""""""
    Return rate of given process.

    * ``proc_nr`` integer representing the requested process.
    * ``return_rate`` writeable real, where the requested rate will be stored.

base/get_species
""""""""""""""""""""""""""""""""""""""""""""""""""
    Return the species that occupies site.

    * ``site`` integer representing the site

base/get_system_name
""""""""""""""""""""""""""""""""""""""""""""""""""
    Return the systems name, that was specified with base/allocate_system

    * ``system_name`` Writeable string of type character(len=200).

base/get_walltime
""""""""""""""""""""""""""""""""""""""""""""""""""
    Return the current walltime.

    * ``return_walltime`` writeable real where the walltime will be stored.

base/increment_procstat
""""""""""""""""""""""""""""""""""""""""""""""""""
    Increment the process counter for process proc by one.

    * ``proc`` integer representing the process to be increment.

base/integ_rates
""""""""""""""""""""""""""""""""""""""""""""""""""
   Stores the time-integrated rates (non-normalized to surface area)
   Used to determine reaction rates, i.e. average number of reactions
   per unit surface and time.
   Let :math:`\mathbf{a}` the integrated rates, :math:`\mathbf{c}` be the
   rate constants, :math:`\mathbf{n}_i` the number of available sites
   during kMC-time interval i,  :math:`\{\Delta t_i\}` the corresponding
   timesteps then :math:`a_{i}(t)` at the time :math:`t=\sum_{i=1}\Delta t_i`
   is calculated according to :math:`a_{i}(t)=\sum_{i=1} c_{i} n_{i}\Delta t_i`.

base/interval_search_real
""""""""""""""""""""""""""""""""""""""""""""""""""
   This is basically a standard binary search algorithm that expects an array
   of ascending real numbers and a scalar real and return the key of the
   corresponding field, with the following modification :

   * the value of the returned field is equal of larger of the given
     value. This is important because the given value is between 0 and the
     largest value in the array and otherwise the last field is never
     selected.
   * if two or more values in the array are identical, the function
     return the index of the leftmost of those field. This is important
     because having field with identical values means that all field except
     the leftmost one do not contain any sites. Refer to
     update_accum_rate to understand why.
   * the value of the returned field may no be zero. Therefore the index
     the to be equal or larger than the first non-zero field.

   However: as everyone knows the binary search is trickier than it appears
   at first site especially real numbers. So intensive testing is
   suggested here!

   * ``arr`` real array of type rsingle (kind_values.f90) in monotonically (not strictly) increasing order
   * ``value`` real positive number from [0, max_arr_value]

base/kmc_step
""""""""""""""""""""""""""""""""""""""""""""""""""
   Number of kMC steps executed.

base/kmc_time
""""""""""""""""""""""""""""""""""""""""""""""""""
   Simulated kMC time in this run in seconds.

base/kmc_time_step
""""""""""""""""""""""""""""""""""""""""""""""""""
   The time increment of the current kMC step.

base/lattice
""""""""""""""""""""""""""""""""""""""""""""""""""
   Stores the actual physical lattice in a 1d array, where the value
   on each slot represents the species on that site.

   Species constants can be conveniently defined
   in lattice\_... and later used directly in the process list.

base/nr_of_proc
""""""""""""""""""""""""""""""""""""""""""""""""""
   Total number of available processes.

base/nr_of_sites
""""""""""""""""""""""""""""""""""""""""""""""""""
   Stores the number of sites available for each process.

base/procstat
""""""""""""""""""""""""""""""""""""""""""""""""""
   Stores the total number of times each process has been executed
   during one simulation.

base/rates
""""""""""""""""""""""""""""""""""""""""""""""""""
   Stores the rate constants for each process in s^-1.

base/reload_system
""""""""""""""""""""""""""""""""""""""""""""""""""
    Restore state of simulation from \*.reload file as saved by
    save_system(). This function also allocates the system's memory
    so calling allocate_system again, will cause a runtime failure.

    * ``system_name`` string of 200 characters which will make the reload_system look for a file called ./<system_name>.reload
    * ``reloaded`` logical return variable, that is .true. reload of system could be completed successfully, and .false. otherwise.

base/replace_species
""""""""""""""""""""""""""""""""""""""""""""""""""
   Replaces the species at a given site with new_species, given
   that old_species is correct, i.e. identical to the site that
   is already there.

   * ``site`` integer representing the site
   * ``old_species`` integer representing the species to be removed
   * ``new_species`` integer representing the species to be placed

base/reset_site
""""""""""""""""""""""""""""""""""""""""""""""""""
    This function is a higher-level function to reset a site
    as if it never existed. To achieve this the species
    is set to null_species and all available processes
    are stripped from the site via del_proc.

    * ``site`` integer representing the requested site.
    * ``species`` integer representing the species that ought to be at the site, for consistency checks

base/save_system
""""""""""""""""""""""""""""""""""""""""""""""""""
    save_system stores the entire system information in a simple ASCII
    filed names <system_name>.reload. All fields except avail_sites are
    stored in the simple scheme:

        variable value

    In the case of array variables, multiple values are seperated by one or
    more spaces, and the record is terminated with a newline. The variable
    avail_sites is treated slightly differently, since printed on a single
    line it is almost impossible to interpret from the ASCII files. Instead
    each process starts a new line, and the first number on the line stands
    for the process number and the remaining fields, hold the values.

    ``none``

base/set_kmc_time
""""""""""""""""""""""""""""""""""""""""""""""""""
    Sets current kmc_time as rdouble real as defined in kind_values.f90.

    * ``new`` readable real, that the kmc time will be set to

base/set_rate_const
""""""""""""""""""""""""""""""""""""""""""""""""""
  Allows to set the rate constant of the process with the number proc_nr.

  * ``proc_n`` The process number as defined in the corresponding proclist\_ module.
  * ``rate`` the rate in :math:`s^{-1}`

base/set_system_name
""""""""""""""""""""""""""""""""""""""""""""""""""
    Set the systems name. Useful in conjunction with base.save_system
    to save \*.reload files under a different name than the default one.

    * ``system_name`` Readable string of type character(len=200).

base/start_time
""""""""""""""""""""""""""""""""""""""""""""""""""
   CPU time spent in simulation at least reload.

base/system_name
""""""""""""""""""""""""""""""""""""""""""""""""""
   Unique indentifier of this simulation to be used for restart files.
   This name should not contain any characters that you don't want to
   have in a filename either, i.e. only [A-Za-z0-9\_-].

base/update_accum_rate
""""""""""""""""""""""""""""""""""""""""""""""""""
    Updates the vector of accum_rates.

    ``none``

base/update_clocks
""""""""""""""""""""""""""""""""""""""""""""""""""
    Updates walltime, kmc_step and kmc_time.

    * ``ran_time`` Random real number :math:`\in [0,1]`

base/update_integ_rate
""""""""""""""""""""""""""""""""""""""""""""""""""
    Updates the vector of integ_rates.

    ``none``

base/volume
""""""""""""""""""""""""""""""""""""""""""""""""""
   Total number of sites.

base/walltime
""""""""""""""""""""""""""""""""""""""""""""""""""
   Total CPU time spent on this simulation.
