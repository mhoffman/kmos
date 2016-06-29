module proclist
use kind_values
use base, only: &
    update_accum_rate, &
    update_integ_rate, &
    determine_procsite, &
    update_clocks, &
    avail_sites, &
    null_species, &
    increment_procstat

use lattice, only: &
    ruo2, &
    ruo2_bridge, &
    ruo2_cus, &
    allocate_system, &
    nr2lattice, &
    lattice2nr, &
    add_proc, &
    can_do, &
    set_rate_const, &
    replace_species, &
    del_proc, &
    reset_site, &
    system_size, &
    spuck, &
    get_species
use run_proc_0000; use nli_0000
use run_proc_0001; use nli_0001
use run_proc_0002; use nli_0002
use run_proc_0003; use nli_0003
use run_proc_0004; use nli_0004
use run_proc_0005; use nli_0005
use run_proc_0006; use nli_0006
use run_proc_0007; use nli_0007
use run_proc_0008; use nli_0008
use run_proc_0009; use nli_0009
use run_proc_0010; use nli_0010
use run_proc_0011; use nli_0011
use run_proc_0012; use nli_0012
use run_proc_0013; use nli_0013
use run_proc_0014; use nli_0014
use run_proc_0015; use nli_0015
use run_proc_0016; use nli_0016
use run_proc_0017; use nli_0017
use run_proc_0018; use nli_0018
use run_proc_0019; use nli_0019
use run_proc_0020; use nli_0020
use run_proc_0021; use nli_0021
use run_proc_0022; use nli_0022
use run_proc_0023; use nli_0023
use run_proc_0024; use nli_0024
use run_proc_0025; use nli_0025
use run_proc_0026; use nli_0026
use run_proc_0027; use nli_0027
use run_proc_0028; use nli_0028
use run_proc_0029; use nli_0029
use run_proc_0030; use nli_0030
use run_proc_0031; use nli_0031
use run_proc_0032; use nli_0032
use run_proc_0033; use nli_0033
use run_proc_0034; use nli_0034
use run_proc_0035; use nli_0035

implicit none
integer(kind=iint), parameter, public :: representation_length = 0
integer(kind=iint), public :: seed_size = 12
integer(kind=iint), public :: seed ! random seed
integer(kind=iint), public, dimension(:), allocatable :: seed_arr ! random seed


integer(kind=iint), parameter, public :: nr_of_proc = 36

character(len=7), parameter, public :: backend = "lat_int"

contains

subroutine run_proc_nr(proc, nr_cell)
    integer(kind=iint), intent(in) :: nr_cell
    integer(kind=iint), intent(in) :: proc

    integer(kind=iint), dimension(4) :: cell

    cell = nr2lattice(nr_cell, :) + (/0, 0, 0, -1/)
    call increment_procstat(proc)

    select case(proc)
    case(oxygen_diffusion_bridge_bridge_down)
        call run_proc_oxygen_diffusion_bridge_bridge_down(cell)
    case(oxygen_diffusion_cus_bridge_right)
        call run_proc_oxygen_diffusion_cus_bridge_right(cell)
    case(co_diffusion_bridge_cus_left)
        call run_proc_co_diffusion_bridge_cus_left(cell)
    case(co_diffusion_cus_cus_up)
        call run_proc_co_diffusion_cus_cus_up(cell)
    case(co_diffusion_bridge_bridge_down)
        call run_proc_co_diffusion_bridge_bridge_down(cell)
    case(reaction_oxygen_bridge_co_cus_left)
        call run_proc_reaction_oxygen_bridge_co_cus_left(cell)
    case(co_desorption_cus)
        call run_proc_co_desorption_cus(cell)
    case(reaction_oxygen_bridge_co_bridge_up)
        call run_proc_reaction_oxygen_bridge_co_bridge_up(cell)
    case(oxygen_desorption_bridge_bridge)
        call run_proc_oxygen_desorption_bridge_bridge(cell)
    case(oxygen_adsorption_bridge_bridge)
        call run_proc_oxygen_adsorption_bridge_bridge(cell)
    case(co_diffusion_bridge_cus_right)
        call run_proc_co_diffusion_bridge_cus_right(cell)
    case(oxygen_adsorption_cus_cus)
        call run_proc_oxygen_adsorption_cus_cus(cell)
    case(co_diffusion_cus_bridge_left)
        call run_proc_co_diffusion_cus_bridge_left(cell)
    case(oxygen_desorption_bridge_cus_left)
        call run_proc_oxygen_desorption_bridge_cus_left(cell)
    case(co_diffusion_cus_cus_down)
        call run_proc_co_diffusion_cus_cus_down(cell)
    case(reaction_oxygen_cus_co_bridge_right)
        call run_proc_reaction_oxygen_cus_co_bridge_right(cell)
    case(co_diffusion_bridge_bridge_up)
        call run_proc_co_diffusion_bridge_bridge_up(cell)
    case(reaction_oxygen_cus_co_cus_up)
        call run_proc_reaction_oxygen_cus_co_cus_up(cell)
    case(reaction_oxygen_cus_co_cus_down)
        call run_proc_reaction_oxygen_cus_co_cus_down(cell)
    case(oxygen_diffusion_bridge_cus_right)
        call run_proc_oxygen_diffusion_bridge_cus_right(cell)
    case(oxygen_diffusion_cus_bridge_left)
        call run_proc_oxygen_diffusion_cus_bridge_left(cell)
    case(oxygen_diffusion_cus_cus_up)
        call run_proc_oxygen_diffusion_cus_cus_up(cell)
    case(reaction_oxygen_bridge_co_cus_right)
        call run_proc_reaction_oxygen_bridge_co_cus_right(cell)
    case(co_diffusion_cus_bridge_right)
        call run_proc_co_diffusion_cus_bridge_right(cell)
    case(oxygen_adsorption_bridge_cus_right)
        call run_proc_oxygen_adsorption_bridge_cus_right(cell)
    case(oxygen_diffusion_bridge_bridge_up)
        call run_proc_oxygen_diffusion_bridge_bridge_up(cell)
    case(oxygen_diffusion_bridge_cus_left)
        call run_proc_oxygen_diffusion_bridge_cus_left(cell)
    case(oxygen_diffusion_cus_cus_down)
        call run_proc_oxygen_diffusion_cus_cus_down(cell)
    case(reaction_oxygen_cus_co_bridge_left)
        call run_proc_reaction_oxygen_cus_co_bridge_left(cell)
    case(reaction_oxygen_bridge_co_bridge_down)
        call run_proc_reaction_oxygen_bridge_co_bridge_down(cell)
    case(oxygen_adsorption_bridge_cus_left)
        call run_proc_oxygen_adsorption_bridge_cus_left(cell)
    case(oxygen_desorption_cus_cus)
        call run_proc_oxygen_desorption_cus_cus(cell)
    case(co_desorption_bridge)
        call run_proc_co_desorption_bridge(cell)
    case(oxygen_desorption_bridge_cus_right)
        call run_proc_oxygen_desorption_bridge_cus_right(cell)
    case(co_adsorption_bridge)
        call run_proc_co_adsorption_bridge(cell)
    case(co_adsorption_cus)
        call run_proc_co_adsorption_cus(cell)
    case default
        print *, "Whoops, should not get here!"
        print *, "PROC_NR", proc
        stop
    end select

end subroutine run_proc_nr

subroutine touchup_cell(cell)
    integer(kind=iint), intent(in), dimension(4) :: cell

    integer(kind=iint), dimension(4) :: site

    integer(kind=iint) :: proc_nr

    site = cell + (/0, 0, 0, 1/)
    do proc_nr = 1, nr_of_proc
        if(avail_sites(proc_nr, lattice2nr(site(1), site(2), site(3), site(4)) , 2).ne.0)then
            call del_proc(proc_nr, site)
        endif
    end do

    call add_proc(nli_oxygen_diffusion_bridge_bridge_down(cell), site)
    call add_proc(nli_oxygen_diffusion_cus_bridge_right(cell), site)
    call add_proc(nli_co_diffusion_bridge_cus_left(cell), site)
    call add_proc(nli_co_diffusion_cus_cus_up(cell), site)
    call add_proc(nli_co_diffusion_bridge_bridge_down(cell), site)
    call add_proc(nli_reaction_oxygen_bridge_co_cus_left(cell), site)
    call add_proc(nli_co_desorption_cus(cell), site)
    call add_proc(nli_reaction_oxygen_bridge_co_bridge_up(cell), site)
    call add_proc(nli_oxygen_desorption_bridge_bridge(cell), site)
    call add_proc(nli_oxygen_adsorption_bridge_bridge(cell), site)
    call add_proc(nli_co_diffusion_bridge_cus_right(cell), site)
    call add_proc(nli_oxygen_adsorption_cus_cus(cell), site)
    call add_proc(nli_co_diffusion_cus_bridge_left(cell), site)
    call add_proc(nli_oxygen_desorption_bridge_cus_left(cell), site)
    call add_proc(nli_co_diffusion_cus_cus_down(cell), site)
    call add_proc(nli_reaction_oxygen_cus_co_bridge_right(cell), site)
    call add_proc(nli_co_diffusion_bridge_bridge_up(cell), site)
    call add_proc(nli_reaction_oxygen_cus_co_cus_up(cell), site)
    call add_proc(nli_reaction_oxygen_cus_co_cus_down(cell), site)
    call add_proc(nli_oxygen_diffusion_bridge_cus_right(cell), site)
    call add_proc(nli_oxygen_diffusion_cus_bridge_left(cell), site)
    call add_proc(nli_oxygen_diffusion_cus_cus_up(cell), site)
    call add_proc(nli_reaction_oxygen_bridge_co_cus_right(cell), site)
    call add_proc(nli_co_diffusion_cus_bridge_right(cell), site)
    call add_proc(nli_oxygen_adsorption_bridge_cus_right(cell), site)
    call add_proc(nli_oxygen_diffusion_bridge_bridge_up(cell), site)
    call add_proc(nli_oxygen_diffusion_bridge_cus_left(cell), site)
    call add_proc(nli_oxygen_diffusion_cus_cus_down(cell), site)
    call add_proc(nli_reaction_oxygen_cus_co_bridge_left(cell), site)
    call add_proc(nli_reaction_oxygen_bridge_co_bridge_down(cell), site)
    call add_proc(nli_oxygen_adsorption_bridge_cus_left(cell), site)
    call add_proc(nli_oxygen_desorption_cus_cus(cell), site)
    call add_proc(nli_co_desorption_bridge(cell), site)
    call add_proc(nli_oxygen_desorption_bridge_cus_right(cell), site)
    call add_proc(nli_co_adsorption_bridge(cell), site)
    call add_proc(nli_co_adsorption_cus(cell), site)
end subroutine touchup_cell

subroutine do_kmc_steps(n)

!****f* proclist/do_kmc_steps
! FUNCTION
!    Performs ``n`` kMC step.
!    If one has to run many steps without evaluation
!    do_kmc_steps might perform a little better.
!    * first update clock
!    * then configuration sampling step
!    * last execute process
!
! ARGUMENTS
!
!    ``n`` : Number of steps to run
!******
    integer(kind=ilong), intent(in) :: n

    integer(kind=ilong) :: i
    real(kind=rsingle) :: ran_proc, ran_time, ran_site
    integer(kind=iint) :: nr_site, proc_nr

    do i = 1, n
    call random_number(ran_time)
    call random_number(ran_proc)
    call random_number(ran_site)
    call update_accum_rate
    call update_clocks(ran_time)

    call update_integ_rate
    call determine_procsite(ran_proc, ran_site, proc_nr, nr_site)
    call run_proc_nr(proc_nr, nr_site)
    enddo

end subroutine do_kmc_steps

subroutine do_kmc_step()

!****f* proclist/do_kmc_step
! FUNCTION
!    Performs exactly one kMC step.
!    *  first update clock
!    *  then configuration sampling step
!    *  last execute process
!
! ARGUMENTS
!
!    ``none``
!******
    real(kind=rsingle) :: ran_proc, ran_time, ran_site
    integer(kind=iint) :: nr_site, proc_nr

    call random_number(ran_time)
    call random_number(ran_proc)
    call random_number(ran_site)
    call update_accum_rate
    call update_clocks(ran_time)

    call update_integ_rate
    call determine_procsite(ran_proc, ran_site, proc_nr, nr_site)
    call run_proc_nr(proc_nr, nr_site)
end subroutine do_kmc_step

subroutine get_next_kmc_step(proc_nr, nr_site)

!****f* proclist/get_kmc_step
! FUNCTION
!    Determines next step without executing it.
!
! ARGUMENTS
!
!    ``none``
!******
    real(kind=rsingle) :: ran_proc, ran_time, ran_site
    integer(kind=iint), intent(out) :: nr_site, proc_nr

    call random_number(ran_time)
    call random_number(ran_proc)
    call random_number(ran_site)
    call update_accum_rate
    call determine_procsite(ran_proc, ran_time, proc_nr, nr_site)

end subroutine get_next_kmc_step

subroutine get_occupation(occupation)

!****f* proclist/get_occupation
! FUNCTION
!    Evaluate current lattice configuration and returns
!    the normalized occupation as matrix. Different species
!    run along the first axis and different sites run
!    along the second.
!
! ARGUMENTS
!
!    ``none``
!******
    ! nr_of_species = 3, spuck = 2
    real(kind=rdouble), dimension(0:2, 1:2), intent(out) :: occupation

    integer(kind=iint) :: i, j, k, nr, species

    occupation = 0

    do k = 0, system_size(3)-1
        do j = 0, system_size(2)-1
            do i = 0, system_size(1)-1
                do nr = 1, spuck
                    ! shift position by 1, so it can be accessed
                    ! more straightforwardly from f2py interface
                    species = get_species((/i,j,k,nr/))
                    if(species.ne.null_species) then
                    occupation(species, nr) = &
                        occupation(species, nr) + 1
                    endif
                end do
            end do
        end do
    end do

    occupation = occupation/real(system_size(1)*system_size(2)*system_size(3))
end subroutine get_occupation

subroutine init(input_system_size, system_name, layer, seed_in, no_banner)

!****f* proclist/init
! FUNCTION
!     Allocates the system and initializes all sites in the given
!     layer.
!
! ARGUMENTS
!
!    * ``input_system_size`` number of unit cell per axis.
!    * ``system_name`` identifier for reload file.
!    * ``layer`` initial layer.
!    * ``no_banner`` [optional] if True no copyright is issued.
!******
    integer(kind=iint), intent(in) :: layer, seed_in
    integer(kind=iint), dimension(2), intent(in) :: input_system_size

    character(len=400), intent(in) :: system_name

    logical, optional, intent(in) :: no_banner

    if (.not. no_banner) then
        print *, "+------------------------------------------------------------+"
        print *, "|                                                            |"
        print *, "| This kMC Model 'my_model' was written by                   |"
        print *, "|                                                            |"
        print *, "|           Max J. Hoffmann (mjhoffmann@gmail.com)           |"
        print *, "|                                                            |"
        print *, "| and implemented with the help of kmos,                     |"
        print *, "| which is distributed under GNU/GPL Version 3               |"
        print *, "| (C) Max J. Hoffmann mjhoffmann@gmail.com                   |"
        print *, "|                                                            |"
        print *, "| kmos is distributed in the hope that it will be useful     |"
        print *, "| but WIHTOUT ANY WARRANTY; without even the implied         |"
        print *, "| waranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR     |"
        print *, "| PURPOSE. See the GNU General Public License for more       |"
        print *, "| details.                                                   |"
        print *, "|                                                            |"
        print *, "| If using kmos for a publication, attribution is            |"
        print *, "| greatly appreciated.                                       |"
        print *, "| Hoffmann, M. J., Matera, S., & Reuter, K. (2014).          |"
        print *, "| kmos: A lattice kinetic Monte Carlo framework.             |"
        print *, "| Computer Physics Communications, 185(7), 2138-2150.        |"
        print *, "|                                                            |"
        print *, "| Development http://mhoffman.github.org/kmos                |"
        print *, "| Documentation http://kmos.readthedocs.org                  |"
        print *, "| Reference http://dx.doi.org/10.1016/j.cpc.2014.04.003      |"
        print *, "|                                                            |"
        print *, "+------------------------------------------------------------+"
        print *, ""
        print *, ""
    endif
    call allocate_system(nr_of_proc, input_system_size, system_name)
    call initialize_state(layer, seed_in)
end subroutine init

subroutine initialize_state(layer, seed_in)

!****f* proclist/initialize_state
! FUNCTION
!    Initialize all sites and book-keeping array
!    for the given layer.
!
! ARGUMENTS
!
!    * ``layer`` integer representing layer
!******
    integer(kind=iint), intent(in) :: layer, seed_in

    integer(kind=iint) :: i, j, k, nr
    ! initialize random number generator
    allocate(seed_arr(seed_size))
    seed = seed_in
    seed_arr = seed
    call random_seed(seed_size)
    call random_seed(put=seed_arr)
    deallocate(seed_arr)
    do k = 0, system_size(3)-1
        do j = 0, system_size(2)-1
            do i = 0, system_size(1)-1
                do nr = 1, spuck
                    call reset_site((/i, j, k, nr/), null_species)
                end do
                select case(layer)
                case (ruo2)
                    call replace_species((/i, j, k, ruo2_bridge/), null_species, default_species)
                    call replace_species((/i, j, k, ruo2_cus/), null_species, default_species)
                end select
            end do
        end do
    end do

    do k = 0, system_size(3)-1
        do j = 0, system_size(2)-1
            do i = 0, system_size(1)-1
                call touchup_cell((/i, j, k, 0/))
            end do
        end do
    end do


end subroutine initialize_state

end module proclist
