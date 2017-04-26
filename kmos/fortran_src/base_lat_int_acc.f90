!/* ROBODOC this makes robodoc to document this file */
#include "assert.ppc"
! Copyright (C) 2009-2013 Max J. Hoffmann
!
! This file is part of kmos.
!
! kmos is free software; you can redistribute it and/or modify
! it under the terms of the GNU General Public License as published by
! the Free Software Foundation; either version 2 of the License, or
! (at your option) any later version.
!
! kmos is distributed in the hope that it will be useful,
! but WITHOUT ANY WARRANTY; without even the implied warranty of
! MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
! GNU General Public License for more details.
!
! You should have received a copy of the GNU General Public License
! along with kmos; if not, write to the Free Software
! Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301
! USA

!****h* kmos/base
! FUNCTION
!    The base kMC module, which implements the kMC method on a :math:`d = 1`
!    lattice. Virtually any lattice kMC model can be build on top of this.
!    The methods offered are:
!
!    * de/allocation of memory
!    * book-keeping of the lattice configuration and all available processes
!    * updating and tracking kMC time, kMC step and wall time
!    * saving and reloading the current state
!    * determine the process and site to be executed
!
!******
module base
use kind_values
!------ No implicit definition of variables !
implicit none

!------ All variables, function and subroutine are private by default
private



! The following subroutines and functions are made public
public :: add_proc, &
  allocate_system, &
  assertion_fail, &
  can_do, &
  deallocate_system, &
  del_proc, &
  determine_procsite, &
  replace_species, &
  get_accum_rate, &
  get_integ_rate, &
  get_avail_site, &
  get_kmc_step, &
  get_kmc_time, &
  set_kmc_time, &
  set_system_name, &
  get_kmc_time_step, &
  get_nrofsites, &
  get_procstat, &
  get_rate, &
  get_species, &
  get_system_name, &
  get_walltime, &
  get_volume , &
  increment_procstat, &
  interval_search_real, &
  is_allocated, &
  null_species, &
  reload_system, &
  reset_site, &
  save_system, &
  set_rate_const, &
  set_null_species, &
  get_null_species, &
  update_accum_rate, &
  update_integ_rate, &
  update_clocks, &
  update_integ_rate_sb, &
  update_eq_proc, &
  check_proc_eq, &
  unscale_reactions, &
  scale_reactions, &
  set_original_rate_const, &
  initialize_proc_pair_index, &
  initialize_reverse_index, &
  set_buffer_parameter, &
  get_buffer_parameter, &
  set_threshold_parameter, &
  get_threshold_parameter, &
  get_execution_steps, &
  get_scaling_factor, &
  get_ave_scaling_factor, &
  set_debug_level, &
  update_sum_sf, &
  get_last_set_scaling_factor, &
  initialize_is_diff_proc, &
  initialize_pair_is_eq, &
  get_save_limit, &
  save_execution, &
  get_saved_execution, &
  get_saved_scaling_factor, &
  reset_saved_execution_data


! Public constants
integer(kind=iint) :: null_species = -1

!---- Allocatable, module wide, variables
integer(kind=iint), dimension(:,:,:), allocatable, public :: avail_sites
!****v* base/avail_sites
! FUNCTION
!   Main book-keeping array that stores for each process the sites
!   that are available and for each site the address
!   in this very array. The meaning of the fields are:
!
!       avail_sites(proc, field, switch)
!
!   where:
!
!   * proc -- refers to a process in the process list
!   * the field within the process, but the meaning differs as explained
!     under 'switch'
!   * switch -- can be either 1 or 2 and switches between
!     (1) the actual numbers of the sites, which are available
!     and filled in from the left but in whatever order they come
!     or (2) the location where the site is stored in (1).
!
!******
integer(kind=iint), dimension(:), allocatable :: lattice
!****v* base/lattice
! FUNCTION
!   Stores the actual physical lattice in a 1d array, where the value
!   on each slot represents the species on that site.
!
!   Species constants can be conveniently defined
!   in lattice\_... and later used directly in the process list.
!******
real(kind=rdouble), dimension(:), allocatable :: accum_rates
!****v* base/accum_rates
! FUNCTION
!   Stores the accumulated rate constant multiplied with the number
!   of sites available for that process to be used by determine_procsite.
!   Let :math:`\mathbf{c}` be the rate constants :math:`\mathbf{n}`
!   the number of available sites, and :math:`\mathbf{a}`
!   the accumulated rates, then :math:`a_{i}`
!   is calculated according to :math:`a_{i}=\sum_{j=1}^{i} c_{j} n_{j}`.
!
!******
!------ S. Matera 09/18/2012------
real(kind=rdouble), dimension(:), allocatable :: integ_rates
!****v* base/integ_rates
! FUNCTION
!   Stores the time-integrated rates (non-normalized to surface area)
!   Used to determine reaction rates, i.e. average number of reactions
!   per unit surface and time.
!   Let :math:`\mathbf{a}` the integrated rates, :math:`\mathbf{c}` be the
!   rate constants, :math:`\mathbf{n}_i` the number of available sites
!   during kMC-time interval i,  :math:`\{\Delta t_i\}` the corresponding
!   timesteps then :math:`a_{i}(t)` at the time :math:`t=\sum_{i=1}\Delta t_i`
!   is calculated according to :math:`a_{i}(t)=\sum_{i=1}} c_{i} n_{i}\Delta t_i`.
!
!******
!------ S. Matera 09/18/2012------
integer(kind=iint), dimension(:), allocatable :: nr_of_sites
!****v* base/nr_of_sites
! FUNCTION
!   Stores the number of sites available for each process.
!******
real(kind=rdouble), dimension(:), allocatable :: rates
!****v* base/rates
! FUNCTION
!   Stores the rate constants for each process in s^-1.
!******
integer(kind=ilong), dimension(:), allocatable :: procstat
!****v* base/procstat
! FUNCTION
!   Stores the total number of times each process has been executed
!   during one simulation.
!******
integer(kind=iint), dimension(:), allocatable :: proc_pair_indices
!****v* base/proc_pair_indices
! FUNCTION
!   Stores the index of each proc in the lists that hold information
!   about the pair processes in the temporal acceleration scheme.
!   The sign of the index is positive for forward reactions and negative
!   for reverse reactions.
!******
integer(kind=iint), dimension(:), allocatable :: reverse_indices
!****v* base/reverse_indices
! FUNCTION
!   For each process index, proc, this array stores the index of the
!   reverse process in proclist.
!******
real(kind=rdouble), dimension(:), allocatable :: original_rates
!****v* base/original_rates
! FUNCTION
!   Stores the original (unmodified) rate constants for each process 
!   in s^-1 in the temporal acceleration scheme.
!******
real(kind=rdouble), dimension(:), allocatable :: integ_rates_sb
!****v* base/integ_rates_sb
! FUNCTION
!   Stores the time-integrated rates (non-normalized to surface area)
!   evaluated within the current superbasin.
!   integ_rates_sb is reset to zeros whenever the system exits the
!   current superbasin as a consequence of the execution of an 
!   irreversible process.
!   integ_rates_sb is calculated using the non-scaled (original) rates.
!   It is used to determine the appropriate scaling factors for each
!   proc at the end of each sampling period in the temporal acceleration 
!   scheme.
!******
integer(kind=iint), dimension(:), allocatable :: procstat_eq
!****v* base/procstat_eq
! FUNCTION
!   Out of the last :math:`\mathbf{n}_e` executions of either
!   the forward or the reverse of a proc, this array stores
!   the number of executions separately for the forward and the
!   reverse of each pair in the temporal acceleration scheme.
!   The sum of the number of forward and reverse executions
!   of each proc pair should always be smaller then or equal
!   to :math:`\mathbf{n}_e`.
!******
logical, dimension(:), allocatable :: pair_is_eq
!****v* base/pair_is_eq
! FUNCTION
!   Stores a logical for each proc pair that is true if proc pair 
!   is equilibrated and false if proc pair is non-equilibrated 
!   in the temporal acceleration scheme.
!******
logical, dimension(:), allocatable :: pair_is_loc_eq
!****v* base/pair_is_loc_eq
! FUNCTION
!   Stores a logical for each proc pair that is true if proc pair 
!   is locally equilibrated (at least :math:`\mathbf{n}_e` executions
!   have occured within the current superbsin) and false if proc pair 
!   is not locally equilibrated in the temporal acceleration scheme.
!******
logical, dimension(:), allocatable :: is_diff_proc
!****v* base/is_diff_proc
! FUNCTION
!   Stores a logical for each proc that is True if the process is a
!   diffusion process and otherwise False.
!******
real(kind=rdouble), dimension(:), allocatable :: scaling_factors
!****v* base/scaling_factors
! FUNCTION
!   Stores the scaling factors for each proc pair in the
!   temporal acceleration scheme.
!******
real(kind=rdouble), dimension(:), allocatable :: last_set_scaling_factors
!****v* base/last_set_scaling_factors
! FUNCTION
!   Stores the value of the scaling factor that was last set during the 
!   scale_reaction subroutine (=0 if never set) for each proc pair in the
!   temporal acceleration scheme.
!******
real(kind=rdouble), dimension(:), allocatable :: sum_sf
!****v* base/sum_sf
! FUNCTION
!   Stores the accumulated scaling factors, that is, for each kmc step and
!   for each process the scaling factor used during that step is added to the
!   value. This array gets updated every time the scaling factors change, that 
!   is, every time scale_reactions or unscale_reactions is called in the
!   temporal acceleration scheme.
!******
integer(kind=ibyte), dimension(:,:), allocatable :: proc_pair_exec
!****v* base/proc_pair_exec
! FUNCTION
!   For each proc pair this array stores a list with integers
!   keeping track of the sequence of forward and reverse
!   executions within the last :math:`\mathbf{n}_e` executions 
!   of either the forward or the reverse of a proc.
!   Initially it is filled with zeros and the pointer stored in
!   pointers_exec points to the first value of the list.
!   Everytime a forward (reverse) of proc proc_nr is executed 
!   the value at the position of the pointer in the list 
!   corresponding to the proc_nr is replaced with 1 (-1) and the 
!   pointer is moved one step forward.
!   If the pointer reaches the end of the list it is moved to the
!   beginning of the list in a cyclic fashion.
!   One is added to the corresponding number of forward (reverse) 
!   executions in procstat_eq.
!   If the replaced value is zero no further book-keeping is done.
!   If the replaced value is 1 (-1) one is subtracted from the 
!   corresponding number of forward (reverse) executions in 
!   procstat_eq.
!******
integer(kind=iint), dimension(:), allocatable :: pointers_exec
!****v* base/pointers_exec
! FUNCTION
!   Stores the index for each proc pair that points to the next
!   element to be replaced (the oldest executed step) in 
!   proc_pair_exec.
!******
integer(kind=ilong), dimension(:), allocatable :: proc_pair_exec_sb
!****v* base/proc_pair_exec_sb
! FUNCTION
!   For each proc pair this array stores the number of executions 
!   within the current superbasin. It is reset to zeros every time
!   a non-equilibrated reaction occurs (in the unscale_reactions 
!   subroutine).
!******
integer(kind=iint), dimension(:), allocatable :: saved_executions
!****v* base/saved_executions
! FUNCTION
!   Used to store executed processes after a target process
!******
real(kind=rdouble), dimension(:), allocatable :: saved_scaling_factors
!****v* base/saved_scaling_factors
! FUNCTION
!   Used to store scaling factors of executed processes after a target process
!******

real(kind=rdouble) :: kmc_time
!****v* base/kmc_time
! FUNCTION
!   Simulated kMC time in this run in seconds.
!******
real(kind=rsingle) :: walltime
!****v* base/walltime
! FUNCTION
!   Total CPU time spent on this simulation.
!******
real(kind=rsingle) :: start_time
!****v* base/start_time
! FUNCTION
!   CPU time spent in simulation at least reload.
!******
integer(kind=ilong) :: kmc_step
!****v* base/kmc_step
! FUNCTION
!   Number of kMC steps executed.
!******
real(kind=rdouble) :: kmc_time_step
!****v* base/kmc_time_step
! FUNCTION
!   The time increment of the current kMC step.
!******
integer(kind=ishort) :: debug
!****v* base/debug
! FUNCTION
!   If > 0, prints information 
!******


!--- Local copies of variables
integer(kind=iint) :: nr_of_proc
!****v* base/nr_of_proc
! FUNCTION
!   Total number of available processes.
!******
integer(kind=iint) :: volume
!****v* base/volume
! FUNCTION
!   Total number of sites.
!******
character(len=200) :: system_name
!****v* base/system_name
! FUNCTION
!   Unique indentifier of this simulation to be used for restart files.
!   This name should not contain any characters that you don't want to
!   have in a filename either, i.e. only [A-Za-z0-9\_-].
!******
real(kind=rdouble) :: buffer_parameter
!****v* base/buffer_parameter
! FUNCTION
!   Used for the temporal acceleration scheme.
!******
integer(kind=iint) :: execution_steps
!****v* base/execution_steps
! FUNCTION
!   Used for the temporal acceleration scheme.
!******
real(kind=rdouble) :: threshold_parameter
!****v* base/threshold_parameter
! FUNCTION
!   Used for the temporal acceleration scheme.
!******
integer(kind=iint) :: save_limit
!****v* base/save_limit
! FUNCTION
!   Used for the temporal acceleration scheme.
!******

!****************
contains
!****************

subroutine update_eq_proc(proc)
    !****f* base/update_eq_proc
    ! FUNCTION
    !    update_eq_proc updates the book-keeping regarding which reaction pairs
    !    are equilibrated. 
    !
    ! ARGUMENTS
    !
    !    * ``proc`` positive integer that states the process that has just been
    !    executed
    !******
    integer(kind=iint), intent(in) :: proc
    integer(kind=iint) :: pair_index, r_proc, pointer_index
    logical :: forward_proc

    ! Make sure proc_nr is in the right range
    ASSERT(proc.gt.0,"update_eq_proc: proc has to be positive")
    ASSERT(proc.le.nr_of_proc,"update_eq_proc: proc has to be less or equal nr_of_proc.")

    !get index of process pair
    pair_index = abs(proc_pair_indices(proc))

    ! *** This part only to be done for non-diff processes ***
    if (is_diff_proc(proc) .eqv. .false.) then
        !Add 1 to process executions for proc in procstat_eq
        procstat_eq(proc) = procstat_eq(proc) + 1

        !get index of of reverse process
        r_proc = reverse_indices(proc)

        !determine if proc is a forward process.
        !Note that forward processes per definition have positive indices in proc_pair_indices.
        if (proc_pair_indices(proc).gt.0) then
            forward_proc = .true.
        else
            forward_proc = .false.
        endif

        !get the element that is currently pointed to in pointers_exec
        pointer_index = pointers_exec(pair_index)

        !For debugging
        if (debug > 2) then
            print *,"BASE/UPDATE_EQ_PROC/PAIR_INDEX:", pair_index
            print *,"BASE/UPDATE_EQ_PROC/PROC:", proc
            print *,"BASE/UPDATE_EQ_PROC/R_PROC:", r_proc
            print *,"BASE/UPDATE_EQ_PROC/FORWARD_PROC:", forward_proc
            print *,"BASE/UPDATE_EQ_PROC/POINTER_INDEX:", pointer_index
        endif

        !If proc pair has not yet reached :math:`\mathbf{n}_e` executions, 
        !just the proc_pair_exec should be updated.
        if (proc_pair_exec(pair_index,pointer_index).eq.0 .and. forward_proc) then
            proc_pair_exec(pair_index,pointer_index) = 1
        else if (proc_pair_exec(pair_index,pointer_index).eq.0 .and. .not. forward_proc) then
            proc_pair_exec(pair_index,pointer_index) = -1
        !If the oldest executed step was a forward reaction (a 1 in proc_pair_exec),
        !then 1 should be subtracted from the forward process in procstat_eq.
        else if (proc_pair_exec(pair_index,pointer_index).eq.1 .and. forward_proc) then
            procstat_eq(proc) = procstat_eq(proc) - 1
            proc_pair_exec(pair_index,pointer_index) = 1
        else if (proc_pair_exec(pair_index,pointer_index).eq.1 .and. .not. forward_proc) then
            procstat_eq(r_proc) = procstat_eq(r_proc) - 1
            proc_pair_exec(pair_index,pointer_index) = -1
        !If the oldest executed step was a reverse reaction (a -1 in proc_pair_exec),
        !then 1 should be subtracted from the reverse process in procstat_eq.
        else if (proc_pair_exec(pair_index,pointer_index).eq.-1 .and. .not. forward_proc) then
            procstat_eq(proc) = procstat_eq(proc) - 1
            proc_pair_exec(pair_index,pointer_index) = -1
        else if (proc_pair_exec(pair_index,pointer_index).eq.-1 .and. forward_proc) then
            procstat_eq(r_proc) = procstat_eq(r_proc) - 1
            proc_pair_exec(pair_index,pointer_index) = 1
        else
            print *,"Could not update procstat_eq"
            print *,"BASE/UPDATE_EQ_PROC/PROC_PAIR_EXEC(PAIR_INDEX,POINTER_INDEX):", proc_pair_exec(pair_index,pointer_index)
            print *,"BASE/UPDATE_EQ_PROC/FORWARD_PROC:", forward_proc
            stop
        endif

        !For debugging
        if (debug > 2) then
            print *,"BASE/UPDATE_EQ_PROC/PROCSTAT_EQ(PROC):", procstat_eq(proc)
            print *,"BASE/UPDATE_EQ_PROC/PROCSTAT_EQ(R_PROC):", procstat_eq(r_proc)
            print *,"BASE/UPDATE_EQ_PROC/PROC_PAIR_EXEC(PAIR_INDEX,POINTER_INDEX):", proc_pair_exec(pair_index,pointer_index)
            print *,"BASE/UPDATE_EQ_PROC/EQ_ASSESSMENT:", (abs(procstat_eq(proc)-procstat_eq(r_proc))/real(execution_steps))
            print *,"BASE/UPDATE_EQ_PROC/THRESHOLD_PARAMETER:", threshold_parameter
        endif

        !Update pointers_exec
        if (pointer_index.eq.execution_steps) then
            pointers_exec(pair_index) = 1
        else
            pointers_exec(pair_index) = pointers_exec(pair_index) + 1
        endif

        !Do a check on procstat_eq
        ASSERT((procstat_eq(proc)+procstat_eq(r_proc)).le.execution_steps,"update_eq_proc: Execution steps exceeded.")

        !Determine if pair is equilibrated.
        if ((procstat_eq(proc)+procstat_eq(r_proc)).eq.execution_steps .and.  abs(procstat_eq(proc)-procstat_eq(r_proc)).lt.(threshold_parameter*execution_steps)) then
            !For debugging
            if (debug > 0) then
                if (pair_is_eq(pair_index) .eqv. .false.) then
                    print *,""
                    print *,"BASE/UPDATE_EQ_PROC/PROC BECAME EQ.:",proc
                    print *,"BASE/UPDATE_EQ_PROC/EQ_ASSESSMENT:", (abs(procstat_eq(proc)-procstat_eq(r_proc))/real(execution_steps))
                    print *,"BASE/UPDATE_EQ_PROC/THRESHOLD_PARAMETER:", threshold_parameter
                    print *,""

                endif
            endif
            pair_is_eq(pair_index) = .true.
        else
            !For debugging
            if (debug > 0) then
                if (pair_is_eq(pair_index) .eqv. .true.) then
                    print *,""
                    print *,"BASE/UPDATE_EQ_PROC/PROC BECAME NON-EQ.:",proc
                    print *,"BASE/UPDATE_EQ_PROC/EQ_ASSESSMENT:", (abs(procstat_eq(proc)-procstat_eq(r_proc))/real(execution_steps))
                    print *,"BASE/UPDATE_EQ_PROC/THRESHOLD_PARAMETER:", threshold_parameter
                    print *,""
                endif
            endif
            pair_is_eq(pair_index) = .false.
        endif
    endif

    ! *** This part to be done for every process ***
    !Add 1 to process executions in local superbasin for proc pair.
    proc_pair_exec_sb(pair_index) = proc_pair_exec_sb(pair_index) + 1

    !Determine if pair is locally equilibrated.
    if (pair_is_eq(pair_index) .eqv. .true.) then
        if (proc_pair_exec_sb(pair_index).ge.execution_steps) then
            !For debugging
            if (debug > 1) then
                if (pair_is_loc_eq(pair_index) .eqv. .false.) then
                    print *,"BASE/UPDATE_EQ_PROC/PROC BECAME LOC. EQ.:",proc
                endif
            endif
            pair_is_loc_eq(pair_index) = .true.
        endif
    else
        pair_is_loc_eq(pair_index) = .false.
    endif

    !For debugging
    if (debug > 2) then
        print *,"BASE/UPDATE_EQ_PROC/PROC_PAIR_EXEC_SB(PAIR_INDEX):", proc_pair_exec_sb(pair_index)
        print *,"BASE/UPDATE_EQ_PROC/PAIR_IS_EQ(PAIR_INDEX):", pair_is_eq(pair_index)
        print *,"BASE/UPDATE_EQ_PROC/PAIR_IS_LOC_EQ(PAIR_INDEX):", pair_is_loc_eq(pair_index)
    endif
end subroutine update_eq_proc

subroutine check_proc_eq(proc, is_eq)
    !****f* base/check_proc_eq
    ! FUNCTION
    !    Check if the just executed process is equilibrated.
    !
    ! ARGUMENTS
    !    * ``proc`` positive integer that states the process
    !    * ``is_eq`` Return logical that is true if process
    !    is equilibrated.
    !
    !******

    integer(kind=iint), intent(in) :: proc
    logical, intent(out) :: is_eq

    ! Make sure proc_nr is in the right range
    ASSERT(proc.gt.0,"add_proc: proc has to be positive")
    ASSERT(proc.le.nr_of_proc,"add_proc: proc has to be less or equal nr_of_proc.")

    is_eq = pair_is_eq(abs(proc_pair_indices(proc)))
end subroutine check_proc_eq

subroutine scale_reactions
    !****f* base/scale_reactions
    ! FUNCTION
    !    Scale the rate constants of all locally equilibrated reactions, that is,
    !    reactions that have been executed at least :math:`\mathbf{n}_e` times
    !    within the current superbasin.
    !    The scaling factor is calculated from the estimated escape rate of the 
    !    current superbasin and the buffer parameter.
    !******

    real(kind=rdouble) :: escape_rate
    integer(kind=iint) :: i, pair_index, r_proc

    escape_rate = 0.
    do i = 1, nr_of_proc
    pair_index = abs(proc_pair_indices(i))
    if (.not. pair_is_loc_eq(pair_index)) then
        escape_rate = escape_rate + integ_rates_sb(i)
    endif
    enddo

    do i = 1, nr_of_proc
    pair_index = abs(proc_pair_indices(i))
    r_proc = reverse_indices(i)
    if (proc_pair_indices(i).gt.0.) then
        if (pair_is_loc_eq(pair_index)) then
            scaling_factors(pair_index) = min(buffer_parameter*2*escape_rate &
            /(integ_rates_sb(i)+integ_rates_sb(r_proc)),1.)
            last_set_scaling_factors(pair_index) = scaling_factors(pair_index)
            rates(i) = original_rates(i)*scaling_factors(pair_index)
            rates(r_proc) = original_rates(r_proc)*scaling_factors(pair_index)
            !For debugging
            if (debug > 2) then
                print *,"BASE/SCALE_REACTIONS/ESCAPE_RATE:", escape_rate
                print *,"BASE/SCALE_REACTIONS/PROC:", i
                print *,"BASE/SCALE_REACTIONS/R_PROC:", r_proc
                print *,"BASE/SCALE_REACTIONS/PAIR_INDEX:", pair_index
                print *,"BASE/SCALE_REACTIONS/BUFFER_PARAMETER:", buffer_parameter
                print *,"BASE/SCALE_REACTIONS/PAIR_RATE:", integ_rates_sb(i)+integ_rates_sb(r_proc)
                print *,"BASE/SCALE_REACTIONS/SCALING_ASSESSMENT:", (integ_rates_sb(i)+ &
                integ_rates_sb(r_proc))/(2*escape_rate)
                print *,"BASE/SCALE_REACTIONS/SCALING_FACTORS(PAIR_INDEX):", scaling_factors(pair_index)
                print *,""
            endif
        else
            if (scaling_factors(pair_index).ne.1) then
                scaling_factors(pair_index) = 1
                rates(i) = original_rates(i)
                rates(r_proc) = original_rates(r_proc)
            endif
        endif
    endif
    enddo
end subroutine scale_reactions

subroutine unscale_reactions
    !****f* base/unscale_reactions
    ! FUNCTION
    !    Reset the scaling factors for all processes to zero.
    !    This function gets called everytime a non-equilibrated 
    !    process has been executed to make sure that the change 
    !    in system dynamics resulting from the execution of the 
    !    non-equilibrated process will be accurately captured.
    !******

    integer(kind=iint) :: i, pair_index, r_proc


    do i = 1, nr_of_proc
    integ_rates_sb(i) = 0
    pair_index = abs(proc_pair_indices(i))
    r_proc = reverse_indices(i)
    if (proc_pair_indices(i).gt.0.) then
        if (debug > 3) then
            print *,"BASE/UNSCALE_REACTIONS/PROC:", i
            print *,"BASE/UNSCALE_REACTIONS/R_PROC:", r_proc
            print *,"BASE/UNSCALE_REACTIONS/PAIR_INDEX:", pair_index
            print *,"BASE/UNSCALE_REACTIONS/SCALING_FACTORS(PAIR_INDEX):", scaling_factors(pair_index)
            print *,""
        endif
        scaling_factors(pair_index) = 1
        rates(i) = original_rates(i)
        rates(r_proc) = original_rates(r_proc)
        proc_pair_exec_sb(pair_index) = 0
        pair_is_loc_eq(pair_index) = .false.
    endif
    enddo
end subroutine unscale_reactions

subroutine update_sum_sf(counter_sp)
    !****f* base/update_sum_sf
    ! FUNCTION
    !    Update sum_sf based on the current value of the scaling
    !    factors and the number of kmc steps that have been run
    !    with these scaling factors.
    !******
    ! ARGUMENTS
    !    * ``k`` the number of run kmc steps
    !
    !******

    integer(kind=iint), intent(in) :: counter_sp
    integer(kind=iint) :: i

    do i = 1, nr_of_proc/2
    sum_sf(i) = sum_sf(i) + scaling_factors(i) * counter_sp
    enddo
end subroutine update_sum_sf

subroutine initialize_proc_pair_index(proc,ppi)
    !****f* base/initialize_proc_pair_index
    ! FUNCTION
    !    initialize_proc_pair_index initializes the process pair index of
    !    the process proc in proc_pair_indices.
    !    It is called for every process every time a model is reset.
    !
    ! ARGUMENTS
    !
    !    * ``proc`` positive integer that states the process
    !    * ``ppi`` integer that states the process pair index, which is
    !    positive for forward and negative for reverse reactions.
    !******
    integer(kind=iint), intent(in) :: proc, ppi

    proc_pair_indices(proc) = ppi
end subroutine initialize_proc_pair_index

subroutine initialize_reverse_index(proc,rev)
    !****f* base/initialize_reverse_index
    ! FUNCTION
    !    initialize_reverse_index initializes the index of the reverse process 
    !    of process, proc, in reverse_indices
    !    It is called for every process every time a model is reset.
    !
    ! ARGUMENTS
    !
    !    * ``proc`` positive integer that states the process
    !    * ``rev`` positive integer that states the index of the reverse process
    !******
    integer(kind=iint), intent(in) :: proc, rev

    reverse_indices(proc) = rev
end subroutine initialize_reverse_index

subroutine initialize_is_diff_proc(proc,is_diff)
    !****f* base/initialize_is_diff_proc
    ! FUNCTION
    !    initialize_is_diff_proc initializes is_diff_proc.
    !    It is called for every process every time a model is reset.
    !
    ! ARGUMENTS
    !
    !    * ``proc`` positive integer that states the process
    !    * ``is_diff`` logical that states whether the process is a diffusion process.
    !******
    integer(kind=iint), intent(in) :: proc
    logical, intent(in) :: is_diff

    is_diff_proc(proc) = is_diff
end subroutine initialize_is_diff_proc

subroutine initialize_pair_is_eq(ppi,is_diff)
    !****f* base/initialize_pair_is_eq
    ! FUNCTION
    !    initialize_pair_is_eq sets pair_is_eq to True for all
    !    diffusion processes.
    !    It is called for every process every time a model is reset.
    !
    ! ARGUMENTS
    !
    !    * ``ppi`` positive integer that states the index of the process pair.
    !    * ``is_diff`` logical that states whether the process pair is a diffusion process.
    !******
    integer(kind=iint), intent(in) :: ppi
    logical, intent(in) :: is_diff

    pair_is_eq(ppi) = is_diff
end subroutine initialize_pair_is_eq

subroutine save_execution(proc, save_counter)
    !****f* base/save_execution
    ! FUNCTION
    !    save_execution saves information about executed process.
    !
    ! ARGUMENTS
    !
    !    * ``proc`` positive integer that states the process that was executed
    !    * ``save_counter`` positive integer that states the position in the arrays
    !******
    integer(kind=iint), intent(in) :: proc, save_counter
    integer(kind=iint) :: pair_index

    saved_executions(save_counter) = proc
    pair_index = abs(proc_pair_indices(proc))
    saved_scaling_factors(save_counter) = scaling_factors(pair_index)

end subroutine save_execution

subroutine reset_saved_execution_data()
    !****f* base/reset_saved_execution_data
    ! FUNCTION
    !    Resets saved_executions and saved_scaling_factors to 0.
    !******
    integer(kind=iint) :: i
    do i = 1, save_limit
    saved_executions(i) = 0
    saved_scaling_factors(i) = 0
    enddo
end subroutine reset_saved_execution_data

subroutine del_proc(proc, site)
  !****f* base/del_proc
  ! FUNCTION
  !    del_proc delete one process from the main book-keeping array
  !    avail_sites. These book-keeping operations happen in O(1) time with the
  !    help of some more book-keeping overhead. avail_sites stores for each
  !    process all sites that are available. The array for each process is
  !    filled from the left, but sites generally not ordered. With this
  !    determine_procsite can effectively pick the next site and process. On
  !    the other hand a second array (avail_sites(:,:,2) ) holds for each
  !    process and each site, the location where it is stored in
  !    avail_site(:,:,1). If a site needs to be removed this subroutine first
  !    looks up the location via avail_sites(:,:,1) and replaces it with the
  !    site that is stored as the last element for this process.
  !
  ! ARGUMENTS
  !
  !    * ``proc`` positive integer that states the process
  !    * ``site`` positive integer that encodes the site to be manipulated
  !******
  integer(kind=iint), intent(in) :: proc, site

  integer(kind=iint) :: memory_address

  ! Make sure proc_nr is in the right range
  ASSERT(proc.ge.0,"add_proc: proc has to be positive or zero")
  ASSERT(proc.le.nr_of_proc,"add_proc: proc has to be less or equal nr_of_proc.")
  ! Make sure site is in the right range
  ASSERT(site.ge.0,"add_proc: site has to be positive or zero")
  ASSERT(site.le.volume,"base/add_proc: site needs to be in volume")

  if(proc.gt.0)then ! proc == 0, stands for process (group) did not match all
    ! assert consistency
    ASSERT(avail_sites(proc, site, 2) .ne. 0 , "Error: tried to take ability from site that is not there!")

    memory_address = avail_sites(proc, site, 2)
    if(memory_address .lt. nr_of_sites(proc))then
      ! check if we are deleting the last field

      ! move last field to deleted field
      avail_sites(proc, memory_address, 1) = avail_sites(proc, nr_of_sites(proc), 1)
      avail_sites(proc, nr_of_sites(proc), 1) = 0

      ! change address of moved field
      avail_sites(proc, avail_sites(proc, memory_address, 1), 2) = memory_address
    else ! simply deleted last field
      avail_sites(proc, memory_address , 1) = 0
    endif
    ! delete address of deleted field
    avail_sites(proc, site, 2) = 0



    ! decrement nr_of_sites(proc)
    nr_of_sites(proc) = nr_of_sites(proc) - 1
  endif
end subroutine del_proc


subroutine add_proc(proc, site)
  !****f* base/add_proc
  ! FUNCTION
  !    The main idea of this subroutine is described in del_proc. Adding one
  !    process to one capability is programmatically simpler since we can just
  !    add it to the end of the respective array in avail_sites.
  !
  ! ARGUMENTS
  !
  !    * ``proc`` positive integer number that represents the process to be added.
  !    * ``site`` positive integer number that represents the site to be manipulated
  !******
  integer(kind=iint), intent(in) :: proc, site

  ! Make sure proc_nr is in the right range
  ASSERT(proc.ge.0,"base/add_proc: proc has to be positive or zero")
  ASSERT(proc.le.nr_of_proc,"base/add_proc: proc has to be less or equal nr_of_proc.")

  ! Make sure site is in the right range
  ASSERT(site.ge.0,"base/add_proc: site has to be positive or zero")
  ASSERT(site.le.volume,"base/add_proc: site needs to be in volume")

  if(proc.gt.0)then ! proc == 0, stands for process (group) did not match all
    ! assert consistency
    ASSERT(avail_sites(proc, site, 2) == 0, "base/add_proc Error: tried to add ability that is already there")

    ! increment nr_of_sites(proc)
    nr_of_sites(proc) = nr_of_sites(proc) + 1

    ! store site in nr_of_sites(proc)th slot
    avail_sites(proc, nr_of_sites(proc), 1) = site

    ! let address of added site point to nr_of_sites(proc)th slot
    avail_sites(proc, site, 2) = nr_of_sites(proc)
  endif

end subroutine add_proc

pure function can_do(proc, site)
  !****f* base/can_do
  ! FUNCTION
  !    Returns true if 'site' can do 'proc' right now
  !
  ! ARGUMENTS
  !
  !    * ``proc`` integer representing the requested process.
  !    * ``site`` integer representing the requested site.
  !    * ``can`` writeable boolean, where the result will be stored.
  !******
  !---------------I/O variables---------------
  logical :: can_do
  integer(kind=iint), intent(in) :: proc, site

  can_do = avail_sites(proc,site,2).ne.0

end function can_do


subroutine reset_site(site, old_species)
  !****f* base/reset_site
  ! FUNCTION
  !    This function is a higher-level function to reset a site
  !    as if it never existed. To achieve this the species
  !    is set to null_species and all available processes
  !    are stripped from the site via del_proc.
  !
  ! ARGUMENTS
  !
  !    * ``site`` integer representing the requested site.
  !    * ``species`` integer representing the species that ought to be at the site, for consistency checks
  !******
  !---------------I/O variables---------------
  integer(kind=iint), intent(in) :: site, old_species
  !---------------internal variables---------------
  integer(kind=iint) :: proc, species

  species = get_species(site)

  ! Reset species if stated correctly
  if(old_species.eq.species)then
    call replace_species(site, species, null_species)
  else
    print *,'ERROR: base/reset_site: wrong species given'
    print *,'Expected',old_species,'but found',species,'on',site
    stop
  endif

  ! Strip all available capabilities from this site
  do proc = 1, nr_of_proc
    if(can_do(proc, site))then
      call del_proc(proc, site)
    endif
  enddo

end subroutine reset_site


subroutine reload_system(input_system_name, reloaded)
  !****f* base/reload_system
  ! FUNCTION
  !    Restore state of simulation from \*.reload file as saved by
  !    save_system(). This function also allocates the system's memory
  !    so calling allocate_system again, will cause a runtime failure.
  !
  ! ARGUMENTS
  !
  !    * ``system_name`` string of 200 characters which will make the reload_system look for a file called ./<system_name>.reload
  !    * ``reloaded`` logical return variable, that is .true. reload of system could be completed successfully, and .false. otherwise.
  !******
  !---------------I/O variables---------------
  character(len=200), intent(in) :: input_system_name
  logical, intent(out) :: reloaded

  character(len=210) :: filename
  character(len=20) :: label
  character(len=10**6) :: buffer
  integer :: io_state , line, pos, subindex, io

  integer, parameter :: filehandler = 15
  logical :: file_exists


  ! store system name in module variable
  system_name = input_system_name
  ! initialize input/output flag
  io_state = 0
  line = 0

  write(filename,'(a,a)')TRIM(ADJUSTL(system_name)),'.reload'
  inquire(file=trim(adjustl(filename)),exist=file_exists)
  if(.not.file_exists)then
    ! If there is no appropiate *.reload file, we can't reload
    ! anything.
    reloaded = .false.
  else
    ! Open file
    open(filehandler, file = filename)

    ! First parse loop: parse scalar values and system size
    ! to allocate appropriate arrays for 2nd loop
    do while(io_state == 0)
      ! read one line into buffer
      read(filehandler, '(a)', iostat=io_state) buffer
      if(io_state == 0) then
        ! advance line number
        line = line + 1

        ! Shuffle all non-space characters to the left.
        buffer = adjustl(buffer)

        ! Ignore comment lines
        if(buffer(1:1) == '#')then
          cycle
        endif
        ! Find position of first space
        pos = scan(buffer, ' ')
        ! Store everything before pos in label
        label = buffer(1:pos)
        ! Everythings else remains in the buffer
        buffer = buffer(pos+1:)

        ! In the first go we are only interested in the variables that
        ! determine the system's size (in memory)
        select case(label)
        case('nr_of_proc')
          read(buffer, *,iostat=io_state) nr_of_proc
        case('volume')
          read(buffer, *, iostat=io_state) volume
        endselect
      endif
    enddo

    if(io_state>0)then
      print *,"Some read error occured in the first reload loop, investigate!"
      stop
    endif


    call allocate_system(nr_of_proc, volume, system_name, buffer_parameter, threshold_parameter, execution_steps, save_limit)

    ! Second loop: parse the "meat" of data
    rewind(filehandler)
    io_state = 0
    line = 0
    do while(io_state == 0)
      read(filehandler, '(a)', iostat=io_state) buffer
      if(io_state == 0) then
        line = line + 1

        buffer = adjustl(buffer)

        ! Ignore comment lines
        if(buffer(1:1) == '#')then
          cycle
        endif
        pos = scan(buffer, ' ')
        label = buffer(1:pos)
        buffer = buffer(pos+1:)
        select case(label)
        case('kmc_time')
          read(buffer, *, iostat=io_state) kmc_time
        case('walltime')
          read(buffer, *, iostat=io_state) walltime
          start_time = walltime
        case('kmc_step')
          read(buffer, *,iostat=io_state) kmc_step
        case('lattice')
          read(buffer, *, iostat=io_state) lattice
        case('nr_of_sites')
          read(buffer, *, iostat=io_state) nr_of_sites
        case('rates')
          read(buffer, *, iostat=io) rates
        case('procstat')
          read(buffer, *, iostat=io) procstat
          ! The two cases avail_sites and avail_sites_back are
          ! more complicated because the first entry determines the
          ! row and the remainder of the lines is the data
        case('avail_sites')
          buffer = adjustl(buffer)
          pos = scan(buffer, ' ')
          label = buffer(1:pos)
          buffer = buffer(pos+1:)
          buffer = adjustl(buffer)

          read(label, * ,iostat = io_state) subindex
          read(buffer , *, iostat = io) avail_sites(subindex,:,1)

        case('avail_sites_back')
          buffer = adjustl(buffer)
          pos = scan(buffer, ' ')
          label = buffer(1:pos)
          buffer = buffer(pos+1:)
          read(label, *, iostat = io) subindex
          read(buffer , *, iostat = io) avail_sites(subindex,:,2)

        endselect
      endif
    enddo
    if(io_state>0)then
      print *,"Some read error occured in the second reload loop, investigate!"
      stop
    endif

    close(filehandler)

    reloaded = .true.
  endif

end subroutine reload_system


subroutine save_system()
  !****f* base/save_system
  ! FUNCTION
  !    save_system stores the entire system information in a simple ASCII
  !    filed names <system_name>.reload. All fields except avail_sites are
  !    stored in the simple scheme:
  !
  !        variable value
  !
  !    In the case of array variables, multiple values are seperated by one or
  !    more spaces, and the record is terminated with a newline. The variable
  !    avail_sites is treated slightly differently, since printed on a single
  !    line it is almost impossible to interpret from the ASCII files. Instead
  !    each process starts a new line, and the first number on the line stands
  !    for the process number and the remaining fields, hold the values.
  !
  ! ARGUMENTS
  !
  !    ``none``
  !******
  integer, parameter :: filehandler = 15
  character(len=210) :: filename
  integer(kind=iint) :: i, io_state

  character(len=10) :: dummy_string

  write(filename,'(2a)',iostat=io_state) trim(adjustl(system_name)),'.reload'
  open(filehandler, file=filename)
  ! Write scalar fields
  write(filehandler,'(a)')"#Reload file written by kmos. Do not edit manually!"
  write(filehandler,'(a)')"#Scalar variables"
  write(filehandler,'(a,es22.15)')' kmc_time  ',kmc_time
  write(filehandler,'(a,es13.7)')' walltime   ',walltime
  write(filehandler,'(a,i22)')' kmc_step ',kmc_step
  write(filehandler,*)'nr_of_proc ',nr_of_proc
  write(filehandler,*)'volume ',volume

  ! Write array fields
  write(dummy_string,'(i9)') nr_of_proc

  write(filehandler,'(a)')"#Vector variables"
  write(filehandler,'(a,'//trim(adjustl(dummy_string))//'i21)')'procstat ',procstat
  write(filehandler,'(a,'//trim(adjustl(dummy_string))//'i9)')'nr_of_sites ',nr_of_sites
  write(filehandler,'(a,'//trim(adjustl(dummy_string))//'es14.7)')'rates ',rates

  write(dummy_string,'(i9)') volume
  write(filehandler,'(a,'//trim(adjustl(dummy_string))//'i9)')'lattice ',lattice

  ! Avail_sites need one more field than 'volume' because first one describes the row
  write(dummy_string,'(i9)') volume+1
  do i = 1, nr_of_proc
    write(filehandler,'(a,'//trim(adjustl(dummy_string))//'i9)')'avail_sites ',i,avail_sites(i,:,1)
  enddo
  do i = 1, nr_of_proc
    write(filehandler,'(a,'//trim(adjustl(dummy_string))//'i9)')'avail_sites_back ',i,avail_sites(i,:,2)
  enddo



  close(filehandler)

end subroutine save_system


subroutine set_rate_const(proc_nr, rate)
  !****f* base/set_rate_const
  ! FUNCTION
  !  Allows to set the rate constant of the process with the number proc_nr.
  !
  ! ARGUMENTS
  !
  !  * ``proc_n`` The process number as defined in the corresponding proclist\_ module.
  !  * ``rate`` the rate in :math:`s^{-1}`
  !******
  integer(kind=iint), intent(in) :: proc_nr
  real(kind=rdouble), intent(in) :: rate

  ! Make sure proc_nr is in the right range
  ASSERT(proc_nr.gt.0,"base/set_rate_const: proc_nr has to be positive")
  !   * the field within the process, but the meaning differs as explained
  !     under 'switch'
  ASSERT(proc_nr.le.nr_of_proc,"base/set_rate_const: proc_nr less or equal nr_of_proc.")
  rates(proc_nr) = rate

end subroutine set_rate_const

subroutine set_original_rate_const(proc_nr, rate)
    !****f* base/set_original_rate_const
    ! FUNCTION
    !  Allows to set the original rate constant of the process with the number proc_nr.
    !
    ! ARGUMENTS
    !
    !  * ``proc_n`` The process number as defined in the corresponding proclist\_ module.
    !  * ``rate`` the rate in :math:`s^{-1}`
    !******
    integer(kind=iint), intent(in) :: proc_nr
    real(kind=rdouble), intent(in) :: rate

    ! Make sure proc_nr is in the right range
    ASSERT(proc_nr.gt.0,"base/set_rate_const: proc_nr has to be positive")
    !   * the field within the process, but the meaning differs as explained
    !     under 'switch'
    ASSERT(proc_nr.le.nr_of_proc,"base/set_rate_const: proc_nr less or equal nr_of_proc.")
    original_rates(proc_nr) = rate

end subroutine set_original_rate_const

subroutine update_accum_rate()
  !****f* base/update_accum_rate
  ! FUNCTION
  !    Updates the vector of accum_rates.
  !
  ! ARGUMENTS
  !
  !    ``none``
  !******

  integer(kind=iint) :: i

  accum_rates(1)=nr_of_sites(1)*rates(1)
  do i = 2, nr_of_proc
    accum_rates(i)=accum_rates(i-1)+nr_of_sites(i)*rates(i)
  enddo

  ASSERT(accum_rates(nr_of_proc).gt.0.,"base/update_accum_rate found &
    accum_rates(nr_of_proc)=0, so no process is available at all")

end subroutine update_accum_rate

!------ S. Matera 09/18/2012------
subroutine update_integ_rate()
    !****f* base/update_integ_rate
    ! FUNCTION
    !    Updates the vector of integ_rates.
    !
    ! ARGUMENTS
    !
    !    ``none``
    !******

    integer(kind=iint) :: i


    do i = 1, nr_of_proc
        integ_rates(i)=integ_rates(i)+nr_of_sites(i)*rates(i)*kmc_time_step
    enddo

    ASSERT(accum_rates(nr_of_proc).gt.0.,"base/update_accum_rate found"// &
        "accum_rates(nr_of_proc)=0, so no process is available at all")

end subroutine update_integ_rate
!------ S. Matera 09/18/2012------

subroutine update_integ_rate_sb()
    !****f* base/update_integ_rate
    ! FUNCTION
    !    Updates the vector of integ_rates_sb.
    !
    ! ARGUMENTS
    !
    !    ``none``
    !******

    integer(kind=iint) :: i


    do i = 1, nr_of_proc
        integ_rates_sb(i)=integ_rates_sb(i)+nr_of_sites(i)*original_rates(i)*kmc_time_step
    enddo

    ASSERT(accum_rates(nr_of_proc).gt.0.,"base/update_accum_rate found" // &
        "accum_rates(nr_of_proc)=0, so no process is available at all")

end subroutine update_integ_rate_sb

subroutine allocate_system(input_nr_of_proc, input_volume, input_system_name, input_buffer_parameter, input_threshold_parameter, input_execution_steps, input_save_limit)
  !****f* base/allocate_system
  ! FUNCTION
  !   Allocates all book-keeping structures and stores
  !   local copies of system name and size(s):
  !
  ! ARGUMENTS
  !   * ``systen_name`` identifier of this simulation, used as name of punch file
  !   * ``volume`` the total number of sites
  !   * ``nr_of_proc`` the total number of processes
  !   * ``buffer_parameter`` used for temporal acc. scheme.
  !   * ``threshold_parameter`` used for temporal acc. scheme.
  !   * ``execution_steps`` used for temporal acc. scheme.
  !   * ``save_limit`` used for temporal acc. scheme.
  !******
  !---------------I/O variables---------------
  character(len=200), intent(in) :: input_system_name
  integer(kind=iint), intent(in) :: input_volume, input_nr_of_proc, input_execution_steps, input_save_limit
  real(kind=rdouble), intent(in) :: input_threshold_parameter, input_buffer_parameter
  logical :: system_allocated

  system_allocated = .false.


  ! Make sure we have at least one process
  if(input_nr_of_proc.le.0)then
    print *,"kmos/base/allocate_system: there needs to be at least one process in a kMC system"
    stop
  endif

  ! Make sure we have at least one site
  if(input_volume.le.0)then
    print *,"kmos/base/allocate_system: there needs to be at least one site in the system"
    stop
  endif

    ! Do some checks on the temporal acceleration parameters
    if(input_buffer_parameter.lt.0)then
        print *,"kmos/base/allocate_system: buffer_parameter cannot be smaller than 0"
        print *,"Current value is: ", buffer_parameter
        stop
    endif
    if(input_execution_steps.lt.1)then
        print *,"kmos/base/allocate_system: execution_steps cannot be smaller than 1"
        stop
    endif
    if(input_threshold_parameter.lt.0)then
        print *,"kmos/base/allocate_system: threshold_parameter cannot be smaller than 0"
        stop
    endif
    if(input_save_limit.lt.1)then
        print *,"kmos/base/allocate_system: save_limit cannot be smaller than 1"
        stop
    endif

  ! Make sure we don't try to allocate twice
  if(allocated(avail_sites))then
    print *,"kmos/base/allocate_system: Tried to allocate avail_sites twice, please deallocate first"
    system_allocated = .true.
  endif
  if(allocated(lattice))then
    print *,"kmos/base/allocate_system: Tried to allocate lattice twice, please deallocate first"
    system_allocated = .true.
  endif
  if(allocated(nr_of_sites))then
    print *,"kmos/base/allocate_system: Tried to allocate nr_of_sites twice, please deallocate first"
    system_allocated = .true.
  endif
  if(allocated(rates))then
    print *,"kmos/base/allocate_system: Tried to allocate rates twice, please deallocate first"
    system_allocated = .true.
  endif
  if(allocated(accum_rates))then
    print *,"kmos/base/allocate_system: Tried to allocate accum_rates twice, please deallocate first"
    system_allocated = .true.
  endif
!------ S. Matera 09/18/2012------
    if(allocated(integ_rates))then
        print *,"kmos/base/allocate_system: Tried to allocate integ_rates twice, please deallocate first"
        system_allocated = .true.
    endif
!------ S. Matera 09/18/2012------
  if(allocated(procstat))then
    print *,"kmos/base/allocate_system: Tried to allocate procstat twice, please deallocate first"
    system_allocated = .true.
  endif
  if(allocated(proc_pair_indices))then
      print *,"kmos/base/allocate_system: Tried to allocate proc_pair_indices twice, please deallocate first"
      system_allocated = .true.
  endif
  if(allocated(reverse_indices))then
      print *,"kmos/base/allocate_system: Tried to allocate reverse_indices twice, please deallocate first"
      system_allocated = .true.
  endif
  if(allocated(original_rates))then
      print *,"kmos/base/allocate_system: Tried to allocate original_rates twice, please deallocate first"
      system_allocated = .true.
  endif
  if(allocated(integ_rates_sb))then
      print *,"kmos/base/allocate_system: Tried to allocate integ_rates_sb twice, please deallocate first"
      system_allocated = .true.
  endif
  if(allocated(procstat_eq))then
      print *,"kmos/base/allocate_system: Tried to allocate procstat_eq twice, please deallocate first"
      system_allocated = .true.
  endif
  if(allocated(pair_is_eq))then
      print *,"kmos/base/allocate_system: Tried to allocate pair_is_eq twice, please deallocate first"
      system_allocated = .true.
  endif
  if(allocated(pair_is_loc_eq))then
      print *,"kmos/base/allocate_system: Tried to allocate pair_is_loc_eq twice, please deallocate first"
      system_allocated = .true.
  endif
  if(allocated(is_diff_proc))then
      print *,"kmos/base/allocate_system: Tried to allocate is_diff_proc_eq twice, please deallocate first"
      system_allocated = .true.
  endif
  if(allocated(scaling_factors))then
      print *,"kmos/base/allocate_system: Tried to allocate scaling_factors twice, please deallocate first"
      system_allocated = .true.
  endif
  if(allocated(last_set_scaling_factors))then
      print *,"kmos/base/allocate_system: Tried to allocate last_set_scaling_factors twice, please deallocate first"
      system_allocated = .true.
  endif
  if(allocated(sum_sf))then
      print *,"kmos/base/allocate_system: Tried to allocate sum_sf twice, please deallocate first"
      system_allocated = .true.
  endif
  if(allocated(proc_pair_exec))then
      print *,"kmos/base/allocate_system: Tried to allocate proc_pair_exec twice, please deallocate first"
      system_allocated = .true.
  endif
  if(allocated(pointers_exec))then
      print *,"kmos/base/allocate_system: Tried to allocate pointers_exec twice, please deallocate first"
      system_allocated = .true.
  endif
  if(allocated(proc_pair_exec_sb))then
      print *,"kmos/base/allocate_system: Tried to allocate proc_pair_exec_sb twice, please deallocate first"
      system_allocated = .true.
  endif
  if(allocated(saved_executions))then
      print *,"kmos/base/allocate_system: Tried to allocate saved_executions twice, please deallocate first"
      system_allocated = .true.
  endif
  if(allocated(saved_scaling_factors))then
      print *,"kmos/base/allocate_system: Tried to allocate saved_scaling_factors twice, please deallocate first"
      system_allocated = .true.
  endif

  if(.not. system_allocated)then
    ! copy arguments to module variables
    nr_of_proc = input_nr_of_proc
    ASSERT(MOD(nr_of_proc,2).eq.0,"base/allocate_system: nr_of_proc must be even")
    volume = input_volume
    system_name = input_system_name
    buffer_parameter = input_buffer_parameter
    threshold_parameter = input_threshold_parameter
    execution_steps = input_execution_steps
    save_limit = input_save_limit

    ! Set clocks and step counter to 0
    kmc_time = 0.
    walltime = 0.
    start_time = 0.
    kmc_step = 0
    debug = 0

    ! allocate data structures and initialize with 0
    allocate(avail_sites(nr_of_proc, volume, 2))
    avail_sites = 0
    allocate(lattice(volume))
    lattice = null_species
    allocate(nr_of_sites(nr_of_proc))
    nr_of_sites = 0
    allocate(rates(nr_of_proc))
    rates = 0
    allocate(accum_rates(nr_of_proc))
    accum_rates = 0
!------ S. Matera 09/18/2012------
        allocate(integ_rates(nr_of_proc))
        integ_rates = 0
!------ S. Matera 09/18/2012------
    allocate(procstat(nr_of_proc))
    procstat = 0
    allocate(proc_pair_indices(nr_of_proc))
    proc_pair_indices = 0
    allocate(reverse_indices(nr_of_proc))
    reverse_indices = 0
    allocate(original_rates(nr_of_proc))
    original_rates = 0
    allocate(integ_rates_sb(nr_of_proc))
    integ_rates_sb = 0
    allocate(procstat_eq(nr_of_proc))
    procstat_eq = 0
    allocate(pair_is_eq(nr_of_proc/2))
    pair_is_eq = .false.
    allocate(is_diff_proc(nr_of_proc))
    is_diff_proc = .false.
    allocate(pair_is_loc_eq(nr_of_proc/2))
    pair_is_loc_eq = .false.
    allocate(scaling_factors(nr_of_proc/2))
    scaling_factors = 1
    allocate(last_set_scaling_factors(nr_of_proc/2))
    last_set_scaling_factors = 0
    allocate(sum_sf(nr_of_proc/2))
    sum_sf = 0
    allocate(proc_pair_exec(nr_of_proc/2,execution_steps))
    proc_pair_exec = 0
    allocate(pointers_exec(nr_of_proc/2))
    pointers_exec = 1
    allocate(proc_pair_exec_sb(nr_of_proc/2))
    proc_pair_exec_sb = 0
    allocate(saved_executions(save_limit))
    saved_executions = 0
    allocate(saved_scaling_factors(save_limit))
    saved_scaling_factors = 0
  endif


end subroutine allocate_system


subroutine is_allocated(result)
  logical, intent(out) :: result
  result = allocated(avail_sites)
end subroutine is_allocated


subroutine deallocate_system()
  !****f* base/deallocate_system
  ! FUNCTION
  !    Deallocate all allocatable arrays: avail_sites, lattice, rates,
  !    accum_rates, procstat.
  !
  ! ARGUMENTS
  !
  !    ``none``
  !******
  if(allocated(avail_sites))then
    deallocate(avail_sites)
  else
    print *,"Warning: avail_sites was not allocated, tried to deallocate."
  endif
  if(allocated(lattice))then
    deallocate(lattice)
  else
    print *,"Warning: lattice was not allocated, tried to deallocate."
  endif
  if(allocated(nr_of_sites))then
    deallocate(nr_of_sites)
  else
    print *,"Warning: nr_of_sites was not allocated, tried to deallocate."
  endif
  if(allocated(rates))then
    deallocate(rates)
  else
    print *,"Warning: rates was not allocated, tried to deallocate."
  endif
  if(allocated(accum_rates))then
    deallocate(accum_rates)
  else
    print *,"Warning: rates was not allocated, tried to deallocate."
  endif
!------ S. Matera 09/18/2012------
    if(allocated(integ_rates))then
        deallocate(integ_rates)
    else
        print *,"Warning: integ_rates was not allocated, tried to deallocate."
    endif
!------ S. Matera 09/18/2012------
  if(allocated(procstat))then
    deallocate(procstat)
  else
    print *,"Warning: rates was not procstat, tried to deallocate."
  endif
  if(allocated(proc_pair_indices))then
      deallocate(proc_pair_indices)
  else
      print *,"Warning: proc_pair_indices was not allocated, tried to deallocate."
  endif
  if(allocated(reverse_indices))then
      deallocate(reverse_indices)
  else
      print *,"Warning: reverse_indices was not allocated, tried to deallocate."
  endif
  if(allocated(original_rates))then
      deallocate(original_rates)
  else
      print *,"Warning: original_rates was not allocated, tried to deallocate."
  endif
  if(allocated(integ_rates_sb))then
      deallocate(integ_rates_sb)
  else
      print *,"Warning: integ_rates_sb was not allocated, tried to deallocate."
  endif
  if(allocated(procstat_eq))then
      deallocate(procstat_eq)
  else
      print *,"Warning: procstat_eq was not allocated, tried to deallocate."
  endif
  if(allocated(pair_is_eq))then
      deallocate(pair_is_eq)
  else
      print *,"Warning: pair_is_eq was not allocated, tried to deallocate."
  endif
  if(allocated(is_diff_proc))then
      deallocate(is_diff_proc)
  else
      print *,"Warning: is_diff_proc was not allocated, tried to deallocate."
  endif
  if(allocated(pair_is_loc_eq))then
      deallocate(pair_is_loc_eq)
  else
      print *,"Warning: pair_is_loc_eq was not allocated, tried to deallocate."
  endif
  if(allocated(scaling_factors))then
      deallocate(scaling_factors)
  else
      print *,"Warning: scaling_factors was not allocated, tried to deallocate."
  endif
  if(allocated(last_set_scaling_factors))then
      deallocate(last_set_scaling_factors)
  else
      print *,"Warning: last_set_scaling_factors was not allocated, tried to deallocate."
  endif
  if(allocated(sum_sf))then
      deallocate(sum_sf)
  else
      print *,"Warning: sum_sf was not allocated, tried to deallocate."
  endif
  if(allocated(proc_pair_exec))then
      deallocate(proc_pair_exec)
  else
      print *,"Warning: proc_pair_exec was not allocated, tried to deallocate."
  endif
  if(allocated(pointers_exec))then
      deallocate(pointers_exec)
  else
      print *,"Warning: pointers_exec was not allocated, tried to deallocate."
  endif
  if(allocated(proc_pair_exec_sb))then
      deallocate(proc_pair_exec_sb)
  else
      print *,"Warning: proc_pair_exec_sb was not allocated, tried to deallocate."
  endif
  if(allocated(saved_executions))then
      deallocate(saved_executions)
  else
      print *,"Warning: saved_executions was not allocated, tried to deallocate."
  endif
  if(allocated(saved_scaling_factors))then
      deallocate(saved_scaling_factors)
  else
      print *,"Warning: saved_scaling_factors was not allocated, tried to deallocate."
  endif
end subroutine deallocate_system


pure function get_system_name()
  !****f* base/get_system_name
  ! FUNCTION
  !    Return the systems name, that was specified with base/allocate_system
  !
  ! ARGUMENTS
  !
  !    * ``system_name`` Writeable string of type character(len=200).
  !******
  !---------------I/O variables---------------
  character(len=200) :: get_system_name

  get_system_name = system_name
end function get_system_name


subroutine set_system_name(input_system_name)
  !****f* base/set_system_name
  ! FUNCTION
  !    Set the systems name. Useful in conjunction with base.save_system
  !    to save *.reload files under a different name than the default one.
  !
  ! ARGUMENTS
  !
  !    * ``system_name`` Readable string of type character(len=200).
  !******
  character(len=200), intent(in) :: input_system_name

  system_name = input_system_name

end subroutine set_system_name


subroutine set_kmc_time(new_kmc_time)
  !****f* base/set_kmc_time
  ! FUNCTION
  !    Sets current kmc_time as rdouble real as defined in kind_values.f90.
  !
  ! ARGUMENTS
  !
  !    * ``new`` readable real, that the kmc time will be set to
  !******
  !---------------I/O variables---------------
  real(kind=rdouble), intent(in)  :: new_kmc_time

  kmc_time = new_kmc_time

end subroutine set_kmc_time


subroutine get_kmc_time(return_kmc_time)
  !****f* base/get_kmc_time
  ! FUNCTION
  !    Returns current kmc_time as rdouble real as defined in kind_values.f90.
  !
  ! ARGUMENTS
  !
  !    * ``return_kmc_time`` writeable real, where the kmc_time will be stored.
  !******
  !---------------I/O variables---------------
  real(kind=rdouble), intent(out)  :: return_kmc_time

  return_kmc_time = kmc_time

end subroutine get_kmc_time


subroutine get_kmc_time_step(return_kmc_time_step)
  !****f* base/get_kmc_time_step
  ! FUNCTION
  !    Returns current kmc_time_step (the time increment).
  !
  ! ARGUMENTS
  !
  !    * ``return_kmc_step`` writeable integer, where the kmc_time_step will be stored.
  !******
  !---------------I/O variables---------------
  real(kind=rdouble), intent(out) :: return_kmc_time_step

  return_kmc_time_step = kmc_time_step

end subroutine get_kmc_time_step


subroutine get_procstat(proc, return_procstat)
  !****f* base/get_procstat
  ! FUNCTION
  !    Return process counter for process proc as integer.
  !
  ! ARGUMENTS
  !
  !    * ``proc`` integer representing the requested process.
  !    * ``return_procstat`` writeable integer, where the process counter will be stored.
  !******
  !---------------I/O variables---------------
  integer(kind=iint),intent(in) :: proc
  integer(kind=ilong),intent(out) :: return_procstat

  return_procstat = procstat(proc)

end subroutine get_procstat


subroutine get_nrofsites(proc, return_nrofsites)
  !****f* base/get_nrofsites
  ! FUNCTION
  !    Return how many sites are available for a certain process.
  !    Usually used for debugging
  !
  ! ARGUMENTS
  !
  !    * ``proc`` integer  representing the requested process
  !    * ``return_nrofsites`` writeable integer, where nr of sites gets stored
  !******
  integer(kind=iint), intent(in) :: proc
  integer(kind=iint), intent(out) :: return_nrofsites

  return_nrofsites = nr_of_sites(proc)
end subroutine get_nrofsites


subroutine get_avail_site(proc_nr, field, switch, return_avail_site)
  !****f* base/get_avail_site
  ! FUNCTION
  !    Return field from the avail_sites database
  !
  ! ARGUMENTS
  !
  !    * ``proc_nr`` integer representing the requested process.
  !    * ``field`` integer for the site at question
  !    * ``switch`` 1 or 2 for site or storage location
  !******
  !---------------I/O variables---------------
  integer(kind=iint), intent(in) :: proc_nr, field, switch
  integer(kind=iint), intent(out) :: return_avail_site

  return_avail_site = avail_sites(proc_nr, field, switch)

end subroutine get_avail_site


subroutine get_accum_rate(proc_nr, return_accum_rate)
  !****f* base/get_accum_rate
  ! FUNCTION
  !    Return accumulated rate at a given process.
  !
  ! ARGUMENTS
  !
  !    * ``proc_nr`` integer representing the requested process.
  !    * ``return_accum_rate`` writeable real, where the requested accumulated rate will be stored.
  !******
  !---------------I/O variables---------------
  integer(kind=iint), intent(in), optional :: proc_nr
  real(kind=rdouble), intent(out) :: return_accum_rate

  if(.not. present(proc_nr) .or. proc_nr.eq.0) then
    return_accum_rate=accum_rates(nr_of_proc)
  else
    return_accum_rate=accum_rates(proc_nr)
  endif

end subroutine get_accum_rate

!------ S. Matera 09/18/2012------
subroutine get_integ_rate(proc_nr, return_integ_rate)
    !****f* base/get_integ_rate
    ! FUNCTION
    !    Return integrated rate at a given process.
    !
    ! ARGUMENTS
    !
    !    * ``proc_nr`` integer representing the requested process.
    !    * ``return_integ_rate`` writeable real, where the requested integrated rate will be stored.
    !******
    !---------------I/O variables---------------
    integer(kind=iint), intent(in), optional :: proc_nr
    real(kind=rdouble), intent(out) :: return_integ_rate

    if(.not. present(proc_nr) .or. proc_nr.eq.0) then
      return_integ_rate=integ_rates(nr_of_proc)
    else
      return_integ_rate=integ_rates(proc_nr)
    endif

end subroutine get_integ_rate
!------ S. Matera 09/18/2012------

subroutine get_rate(proc_nr, return_rate)
  !****f* base/get_rate
  ! FUNCTION
  !    Return rate of given process.
  !
  ! ARGUMENTS
  !
  !    * ``proc_nr`` integer representing the requested process.
  !    * ``return_rate`` writeable real, where the requested rate will be stored.
  !******
  !---------------I/O variables---------------
  integer(kind=iint), intent(in) :: proc_nr
  real(kind=rdouble), intent(out) :: return_rate

  return_rate=rates(proc_nr)

end subroutine get_rate


subroutine increment_procstat(proc)
  !****f* base/increment_procstat
  ! FUNCTION
  !    Increment the process counter for process proc by one.
  !
  ! ARGUMENTS
  !
  !    * ``proc`` integer representing the process to be increment.
  !******
  integer(kind=iint),intent(in) :: proc

  procstat(proc) = procstat(proc) + 1

end subroutine increment_procstat


subroutine get_walltime(return_walltime)
  !****f* base/get_walltime
  ! FUNCTION
  !    Return the current walltime.
  !
  ! ARGUMENTS
  !
  !    * ``return_walltime`` writeable real where the walltime will be stored.
  !******
  !---------------I/O variables---------------
  real(kind=rsingle), intent(out) :: return_walltime

  return_walltime = walltime

end subroutine get_walltime

subroutine get_volume(return_volume)
  !****f* base/get_kmc_volume
  ! FUNCTION
  !    Return the total number of sites.
  !
  ! ARGUMENTS
  !
  !    * ``volume`` Writeable integer.
  !******
  !---------------I/O variables---------------
  integer(kind=iint), intent(out) :: return_volume

  return_volume = volume

end subroutine get_volume

subroutine get_kmc_step(return_kmc_step)
  !****f* base/get_kmc_step
  ! FUNCTION
  !    Return the current kmc_step
  !
  ! ARGUMENTS
  !
  !    * ``kmc_step`` Writeable integer
  !******
  !---------------I/O variables---------------
  integer(kind=ilong), intent(out) :: return_kmc_step

  return_kmc_step = kmc_step

end subroutine get_kmc_step


subroutine determine_procsite(ran_proc, ran_site, proc, site)
  !****f* base/determine_procsite
  ! FUNCTION
  !    Expects two random numbers between 0 and 1 and determines the
  !    corresponding process and site from accum_rates and avail_sites.
  !    Technically one random number would be sufficient but to circumvent
  !    issues with wrong interval_search_real implementation or rounding
  !    errors I decided to take two random numbers:
  !
  ! ARGUMENTS
  !    * ``ran_proc`` Random real number from :math:`\in[0,1]` that selects the next process
  !    * ``ran_site`` Random real number from :math:`\in[0,1]` that selects the next site
  !    * ``proc`` Return integer :math:`\in[1,\mathrm{nr\_of\_proc}`
  !    * ``site`` Return integer :math:`\in [1,\mathrm{volume}`
  !
  !******
  !---------------I/O variables---------------
  real(kind=rsingle), intent(in) :: ran_proc, ran_site
  integer(kind=iint), intent(out) :: proc, site
  !---------------internal variables---------------


  ASSERT(ran_proc.ge.0,"base/determine_procsite: ran_proc has to be positive")
  ASSERT(ran_proc.le.1,"base/determine_procsite: ran_proc has to be less or equal 1")
  ASSERT(ran_site.ge.0,"base/determine_procsite: ran_site has to be positive")
  ASSERT(ran_site.le.1,"base/determine_procsite: ran_site has to be less or equal 1")

  ! ran_proc <- [0,1] so we multiply with larger value in accum_rates
  call interval_search_real(accum_rates, ran_proc*accum_rates(nr_of_proc), proc)


  ! the result shall be between 1 and  nrofsite(proc) so we have to add 1 the
  ! scaled random number. But if the random number is closer to 1 than machine
  ! precision, e.g. 0.999999999, we would get nrofsits(proc)+1 so we have to
  ! cap it with min(...)
  site =  avail_sites(proc, &
    min(nr_of_sites(proc),int(1+ran_site*(nr_of_sites(proc)))),1)


  ASSERT(nr_of_sites(proc).gt.0,"base/determine_procsite: chosen process is invalid &
    because it has no sites available.")
  ASSERT(site.gt.0,"kmos/base/determine_procsite: tries to return invalid site")
  ASSERT(site.le.volume,"base/determine_procsite: tries to return site larger than volume")


end subroutine determine_procsite


subroutine update_clocks(ran_time)
  !****f* base/update_clocks
  ! FUNCTION
  !    Updates walltime, kmc_step and kmc_time.
  !
  ! ARGUMENTS
  !
  !    * ``ran_time`` Random real number :math:`\in [0,1]`
  !******
  real(kind=rsingle), intent(in) :: ran_time
  real(kind=rsingle) :: runtime


  ! Make sure ran_time is in the right interval
  ASSERT(ran_time.ge.0.,"base/update_clocks: ran_time variable has to be positive.")
  ASSERT(ran_time.le.1.,"base/update_clocks: ran_time variable has to be less than 1.")

  kmc_time_step = -log(ran_time)/accum_rates(nr_of_proc)
  ! Make sure the difference is not so small, that it is rounded off
  ! ASSERT(kmc_time+kmc_time_step>kmc_time,"base/update_clocks: precision of kmc_time is not sufficient")

  call CPU_TIME(runtime)

  ! Make sure we are not dividing by zero
  ASSERT(accum_rates(nr_of_proc).gt.0,"base/update_clocks: total rate was found to be zero")
  kmc_time = kmc_time + kmc_time_step

  ! Increment kMC steps
  kmc_step = kmc_step + 1

  ! Walltime is the time of this simulation run plus the walltime
  ! when the simulation was reloaded, so walltime represents the total
  ! walltime across reloads.
  walltime = start_time + runtime
  !------ S. Matera 09/18/2012------
  !-- 'call update_integ_rate()' directly in do_kmc_step(s)
  ! call update_integ_rate()
  !------ S. Matera 09/18/2012------


end subroutine update_clocks


pure function get_species(site)
  !****f* base/get_species
  ! FUNCTION
  !    Return the species that occupies site.
  !
  ! ARGUMENTS
  !
  !    * ``site`` integer representing the site
  !******
  !---------------I/O variables---------------
  integer(kind=iint) :: get_species
  integer(kind=iint), intent(in) :: site

  !! DEBUG
  !print *, site
  !ASSERT(site.ge.1,"kmos/base/get_species was asked for a zero or negative site")
  !ASSERT(site.le.volume,"kmos/base/get_species was asked for a site outside the lattice")

  get_species = lattice(site)

end function get_species


subroutine replace_species(site, old_species, new_species)
  !****f* base/replace_species
  ! FUNCTION
  !   Replaces the species at a given site with new_species, given
  !   that old_species is correct, i.e. identical to the site that
  !   is already there.
  !
  ! ARGUMENTS
  !
  !   * ``site`` integer representing the site
  !   * ``old_species`` integer representing the species to be removed
  !   * ``new_species`` integer representing the species to be placed
  !******
  integer(kind=iint), intent(in) :: site, old_species, new_species

  ASSERT(site.le.volume,"kmos/base/replace_species was asked for a site outside the lattice")

  ! Double-check that we actually remove the atom that we think is there
  if(old_species.ne.lattice(site))then
    print '(a)', "kmos/base/replace_species Tried to remove species from sites which is not there!"
    print '(a,i2,a,i2)', "Attempted replacement:", old_species, "->", new_species
    print '(a,i2,a,i9,a,i9)', "Found species:", lattice(site),"on site", site,"at step",kmc_step
    print '(a)', "For a more human-readable error message, please run"
    print '(a)', "in a python console"
    print '(a)', "--"
    print '(a)', " "
    print '(a)', "from kmos.run import KMC_Model"
    print '(a)', "model = KMC_Model(banner=False, print_rates=False)"
    print '(a,i2,a,i2,a,i2,a,i10,a,i10,a)', &
      "model.post_mortem(err_code=(",old_species,", ",new_species, ", ",  lattice(site), ", ", site, ", ", kmc_step, "))"
    print '(a)', "model.view()"

    stop
  endif

  lattice(site) = new_species
end subroutine replace_species


subroutine interval_search_real(arr, value, return_field)
  !****f* base/interval_search_real
  ! FUNCTION
  !   This is basically a standard binary search algorithm that expects an array
  !   of ascending real numbers and a scalar real and return the key of the
  !   corresponding field, with the following modification :
  !
  !   * the value of the returned field is equal of larger of the given
  !     value. This is important because the given value is between 0 and the
  !     largest value in the array and otherwise the last field is never
  !     selected.
  !   * if two or more values in the array are identical, the function
  !     return the index of the leftmost of those field. This is important
  !     because having field with identical values means that all field except
  !     the leftmost one do not contain any sites. Refer to
  !     update_accum_rate to understand why.
  !   * the value of the returned field may no be zero. Therefore the index
  !     the to be equal or larger than the first non-zero field.
  !
  !   However: as everyone knows the binary search is trickier than it appears
  !   at first site especially real numbers. So intensive testing is
  !   suggested here!
  !
  ! ARGUMENTS
  !
  !   * ``arr`` real array of type rsingle (kind_values.f90) in monotonically (not strictly) increasing order
  !   * ``value`` real positive number from [0, max_arr_value]
  !
  !******
  !---------------I/O variables---------------
  real(kind=rdouble),dimension(:), intent(in) :: arr
  real(kind=rdouble),intent(in) :: value
  integer(kind=iint), intent(out) :: return_field
  !---------------internal variables---------------
  integer(kind=iint) :: left, mid, right

  left = 1
  right = size(arr)

  binarysearch: do
    ! Determine the middle between left and right by bit shifting
    mid = ISHFT(right+left, -1)

    ! if left and right overlap, we are done for now
    if(left.ge.right)then
      exit binarysearch
    endif
    ! If our value is to the left of the middle, adjust right
    if(value < arr(mid)) then
      right = mid
    else  ! otherwise adjust left.
      left = mid + 1
    endif
    ! So now, we have found a candidate fields, which is great.
    ! We just have to make sure it fullfills all other requirements.
  enddo binarysearch

  ! If the value turns out to be zero, we do a linear search
  ! to the right until we find a non-zero entry
  if(arr(mid).eq.0.)then
    nonzerosearch: do
      if(arr(mid).gt.0.)then
        if(mid.ge.size(arr))then
          print *,""
          print *,""
          print *,"ERROR: interval_search_real can't find available process"
          print *,"This usually means one of the following:"
          print *," - you forgot to define rate constants"
          print *," - you create a dead-lock: e.g. adsorption without corresponding desorption."
          print *," - you started the model in an initial state without transitions"
          stop
        endif
        exit nonzerosearch
      else
        mid = mid + 1
      endif
    enddo nonzerosearch
  endif


  ! If we are here, the value is non-zero which is great, but we also
  ! have to make sure we return the left-most field if one or more fields
  ! have the same value.
  leftmostsearch: do
    if(mid==1)then
      exit leftmostsearch
    endif
    if(arr(mid-1).ge.arr(mid))then
      mid = mid - 1
    else
      exit leftmostsearch
      ASSERT(arr(mid).gt.arr(mid-1),"interval_search_real did not return a leftmost")
    endif
  enddo leftmostsearch


  ASSERT(mid>0,"Returned index has to be at least 1")
  ASSERT(mid<=size(arr),"Returned index can be at most size(arr)")
  ASSERT(arr(mid).gt.0.,"Value of returned field has to be greater then 0")
  ASSERT(value.le.arr(mid),"interval_search_real has an internal error")

  return_field = mid


end subroutine interval_search_real

subroutine assertion_fail(a, r)
  !****f* base/assertion_fail
  ! FUNCTION
  !    Function that shall be used by all parts of the program to print a
  !    proper message in case some assertion fails.
  !
  ! ARGUMENTS
  !
  !    * ``a`` condition that is supposed to hold true
  !    * ``r`` message that is printed to the poor user in case it fails
  !******
  character(*), intent(in)::r, a
  character(len=30)::st, wt, kt
  write(st, '(i0)')kmc_step
  write(wt, '(f0.2)')walltime
  write(kt, '(es10.3)')kmc_time
  write(*,*)'Assertion '//a//' failed: '//r
  write(*,*)' at kmc step: '//trim(st)// &
    ' walltime: '//trim(wt)// &
    '  kmc_time:'//trim(kt)
  stop

end subroutine assertion_fail

subroutine set_null_species(input_null_species)
    integer(kind=iint), intent(in) :: input_null_species

    null_species = input_null_species

end subroutine set_null_species

subroutine get_null_species(output_null_species)
    integer(kind=iint), intent(out) :: output_null_species

    output_null_species = null_species

end subroutine get_null_species

subroutine set_buffer_parameter(input_buffer_parameter)
    real(kind=rdouble), intent(in) :: input_buffer_parameter

    buffer_parameter = input_buffer_parameter

end subroutine set_buffer_parameter

subroutine get_buffer_parameter(output_buffer_parameter)
    real(kind=rdouble), intent(out) :: output_buffer_parameter

    output_buffer_parameter = buffer_parameter

end subroutine get_buffer_parameter

subroutine set_threshold_parameter(input_threshold_parameter)
    real(kind=rdouble), intent(in) :: input_threshold_parameter

    threshold_parameter = input_threshold_parameter

end subroutine set_threshold_parameter

subroutine get_threshold_parameter(output_threshold_parameter)
    real(kind=rdouble), intent(out) :: output_threshold_parameter

    output_threshold_parameter = threshold_parameter

end subroutine get_threshold_parameter

subroutine get_execution_steps(output_execution_steps)
    integer(kind=iint), intent(out) :: output_execution_steps

    output_execution_steps = execution_steps

end subroutine get_execution_steps

subroutine get_save_limit(output_save_limit)
    integer(kind=iint), intent(out) :: output_save_limit

    output_save_limit = save_limit

end subroutine get_save_limit

subroutine get_scaling_factor(pair_index,output_scaling_factor)
    integer(kind=iint), intent(in) :: pair_index
    real(kind=rdouble), intent(out) :: output_scaling_factor

    output_scaling_factor = scaling_factors(pair_index)

end subroutine get_scaling_factor

subroutine get_ave_scaling_factor(pair_index,output_ave_scaling_factor)
    integer(kind=iint), intent(in) :: pair_index
    real(kind=rdouble), intent(out) :: output_ave_scaling_factor

    output_ave_scaling_factor = sum_sf(pair_index) / kmc_step

end subroutine get_ave_scaling_factor

subroutine get_last_set_scaling_factor(pair_index,output_last_set_scaling_factor)
    integer(kind=iint), intent(in) :: pair_index
    real(kind=rdouble), intent(out) :: output_last_set_scaling_factor

    output_last_set_scaling_factor = last_set_scaling_factors(pair_index)

end subroutine get_last_set_scaling_factor

subroutine get_saved_execution(i,output_proc)
    integer(kind=iint), intent(in) :: i
    integer(kind=iint), intent(out) :: output_proc

    output_proc = saved_executions(i) 

end subroutine get_saved_execution

subroutine get_saved_scaling_factor(i,output_sf)
    integer(kind=iint), intent(in) :: i
    real(kind=rdouble), intent(out) :: output_sf
    
    output_sf = saved_scaling_factors(i)

end subroutine get_saved_scaling_factor

subroutine set_debug_level(debug_level)
    integer(kind=ishort), intent(in) :: debug_level
    debug = debug_level
end subroutine set_debug_level


end module base
