module proclist
use kind_values
use base, only: &
    update_accum_rate, &
    update_integ_rate, &
    reaccumulate_rates_matrix, &
    determine_procsite, &
    update_clocks, &
    avail_sites, &
    null_species, &
    increment_procstat

use lattice, only: &
    square, &
    square_default, &
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
    update_rates_matrix, &
    spuck, &
    get_species
use proclist_constants, only: &
    default_species, &
    CO, &
    O, &
    empty, &
    CO_ads, &
    CO_des, &
    CO_oxidation_00, &
    CO_oxidation_01, &
    CO_oxidation_02, &
    CO_oxidation_03, &
    O2_des_right, &
    O2_des_up, &
    O_ads_00, &
    O_ads_01
use proclist_pars, only: &
    gr_CO_ads, &
    gr_CO_des, &
    gr_CO_oxidation_00, &
    gr_CO_oxidation_01, &
    gr_CO_oxidation_02, &
    gr_CO_oxidation_03, &
    gr_O2_des_right, &
    gr_O2_des_up, &
    gr_O_ads_00, &
    gr_O_ads_01
use run_proc_0001
use run_proc_0002
use run_proc_0003
use run_proc_0004
use run_proc_0005
use run_proc_0006
use run_proc_0007
use run_proc_0008
use run_proc_0009
use run_proc_0010

implicit none
integer(kind=iint), parameter, public :: representation_length = 23
integer(kind=iint), public :: seed_size = 12
integer(kind=iint), public :: seed ! random seed
integer(kind=iint), public, dimension(:), allocatable :: seed_arr ! random seed


integer(kind=iint), parameter, public :: nr_of_proc = 10

character(len=3), parameter, public :: backend = "otf"

contains

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
    ! nr_of_species = 3, spuck = 1
    real(kind=rdouble), dimension(0:2, 1:1), intent(out) :: occupation

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
        print *, "| This kMC Model 'IntZGB' was written by                     |"
        print *, "|                                                            |"
        print *, "|           Juan M. Lorenzi (jmlorenzi@gmail.com)            |"
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
                case (square)
                    call replace_species((/i, j, k, square_default/), null_species, default_species)
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

subroutine recalculate_rates_matrix()

    integer(kind=iint) :: i,j,k

    do i=1, system_size(1)
        do j=1, system_size(2)
            do k=1, system_size(3)
                if(can_do(CO_ads,(/ i, j, k, 1/))) then
                    call update_rates_matrix(CO_ads,(/ i, j, k, 1/),gr_CO_ads((/ i, j, k, 0/)))
                end if
            end do
        end do
    end do

    do i=1, system_size(1)
        do j=1, system_size(2)
            do k=1, system_size(3)
                if(can_do(CO_des,(/ i, j, k, 1/))) then
                    call update_rates_matrix(CO_des,(/ i, j, k, 1/),gr_CO_des((/ i, j, k, 0/)))
                end if
            end do
        end do
    end do

    do i=1, system_size(1)
        do j=1, system_size(2)
            do k=1, system_size(3)
                if(can_do(CO_oxidation_00,(/ i, j, k, 1/))) then
                    call update_rates_matrix(CO_oxidation_00,(/ i, j, k, 1/),gr_CO_oxidation_00((/ i, j, k, 0/)))
                end if
            end do
        end do
    end do

    do i=1, system_size(1)
        do j=1, system_size(2)
            do k=1, system_size(3)
                if(can_do(CO_oxidation_01,(/ i, j, k, 1/))) then
                    call update_rates_matrix(CO_oxidation_01,(/ i, j, k, 1/),gr_CO_oxidation_01((/ i, j, k, 0/)))
                end if
            end do
        end do
    end do

    do i=1, system_size(1)
        do j=1, system_size(2)
            do k=1, system_size(3)
                if(can_do(CO_oxidation_02,(/ i, j, k, 1/))) then
                    call update_rates_matrix(CO_oxidation_02,(/ i, j, k, 1/),gr_CO_oxidation_02((/ i, j, k, 0/)))
                end if
            end do
        end do
    end do

    do i=1, system_size(1)
        do j=1, system_size(2)
            do k=1, system_size(3)
                if(can_do(CO_oxidation_03,(/ i, j, k, 1/))) then
                    call update_rates_matrix(CO_oxidation_03,(/ i, j, k, 1/),gr_CO_oxidation_03((/ i, j, k, 0/)))
                end if
            end do
        end do
    end do

    do i=1, system_size(1)
        do j=1, system_size(2)
            do k=1, system_size(3)
                if(can_do(O2_des_right,(/ i, j, k, 1/))) then
                    call update_rates_matrix(O2_des_right,(/ i, j, k, 1/),gr_O2_des_right((/ i, j, k, 0/)))
                end if
            end do
        end do
    end do

    do i=1, system_size(1)
        do j=1, system_size(2)
            do k=1, system_size(3)
                if(can_do(O2_des_up,(/ i, j, k, 1/))) then
                    call update_rates_matrix(O2_des_up,(/ i, j, k, 1/),gr_O2_des_up((/ i, j, k, 0/)))
                end if
            end do
        end do
    end do

    do i=1, system_size(1)
        do j=1, system_size(2)
            do k=1, system_size(3)
                if(can_do(O_ads_00,(/ i, j, k, 1/))) then
                    call update_rates_matrix(O_ads_00,(/ i, j, k, 1/),gr_O_ads_00((/ i, j, k, 0/)))
                end if
            end do
        end do
    end do

    do i=1, system_size(1)
        do j=1, system_size(2)
            do k=1, system_size(3)
                if(can_do(O_ads_01,(/ i, j, k, 1/))) then
                    call update_rates_matrix(O_ads_01,(/ i, j, k, 1/),gr_O_ads_01((/ i, j, k, 0/)))
                end if
            end do
        end do
    end do


    call reaccumulate_rates_matrix()
end subroutine recalculate_rates_matrix
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

    select case(get_species(cell + (/0, 0, 0, square_default/)))
    case(CO)
        call add_proc(CO_des, cell + (/ 0, 0, 0, 1/), gr_CO_des(cell + (/ 0, 0, 0, 0/)))
        select case(get_species(cell + (/1, 0, 0, square_default/)))
        case(O)
            call add_proc(CO_oxidation_00, cell + (/ 0, 0, 0, 1/), gr_CO_oxidation_00(cell + (/ 0, 0, 0, 0/)))
        end select

        select case(get_species(cell + (/0, 1, 0, square_default/)))
        case(O)
            call add_proc(CO_oxidation_01, cell + (/ 0, 0, 0, 1/), gr_CO_oxidation_01(cell + (/ 0, 0, 0, 0/)))
        end select

        select case(get_species(cell + (/-1, 0, 0, square_default/)))
        case(O)
            call add_proc(CO_oxidation_02, cell + (/ 0, 0, 0, 1/), gr_CO_oxidation_02(cell + (/ 0, 0, 0, 0/)))
        end select

        select case(get_species(cell + (/0, -1, 0, square_default/)))
        case(O)
            call add_proc(CO_oxidation_03, cell + (/ 0, 0, 0, 1/), gr_CO_oxidation_03(cell + (/ 0, 0, 0, 0/)))
        end select

    case(O)
        select case(get_species(cell + (/1, 0, 0, square_default/)))
        case(O)
            call add_proc(O2_des_right, cell + (/ 0, 0, 0, 1/), gr_O2_des_right(cell + (/ 0, 0, 0, 0/)))
        end select

        select case(get_species(cell + (/0, 1, 0, square_default/)))
        case(O)
            call add_proc(O2_des_up, cell + (/ 0, 0, 0, 1/), gr_O2_des_up(cell + (/ 0, 0, 0, 0/)))
        end select

    case(empty)
        call add_proc(CO_ads, cell + (/ 0, 0, 0, 1/), gr_CO_ads(cell + (/ 0, 0, 0, 0/)))
        select case(get_species(cell + (/1, 0, 0, square_default/)))
        case(empty)
            call add_proc(O_ads_00, cell + (/ 0, 0, 0, 1/), gr_O_ads_00(cell + (/ 0, 0, 0, 0/)))
        end select

        select case(get_species(cell + (/0, 1, 0, square_default/)))
        case(empty)
            call add_proc(O_ads_01, cell + (/ 0, 0, 0, 1/), gr_O_ads_01(cell + (/ 0, 0, 0, 0/)))
        end select

    end select


end subroutine touchup_cell
subroutine run_proc_nr(proc, nr_cell)

!****f* proclist/run_proc_nr
! FUNCTION
!    Runs process ``proc`` on site ``nr_site``.
!
! ARGUMENTS
!
!    * ``proc`` integer representing the process number
!    * ``nr_site``  integer representing the site
!******
    integer(kind=iint), intent(in) :: proc
    integer(kind=iint), intent(in) :: nr_cell

    integer(kind=iint), dimension(4) :: cell

    call increment_procstat(proc)

    ! lsite = lattice_site, (vs. scalar site)
    cell = nr2lattice(nr_cell, :) + (/0, 0, 0, -1/)

    select case(proc)
    case(CO_ads)
        call run_proc_CO_ads(cell)

    case(CO_des)
        call run_proc_CO_des(cell)

    case(CO_oxidation_00)
        call run_proc_CO_oxidation_00(cell)

    case(CO_oxidation_01)
        call run_proc_CO_oxidation_01(cell)

    case(CO_oxidation_02)
        call run_proc_CO_oxidation_02(cell)

    case(CO_oxidation_03)
        call run_proc_CO_oxidation_03(cell)

    case(O2_des_right)
        call run_proc_O2_des_right(cell)

    case(O2_des_up)
        call run_proc_O2_des_up(cell)

    case(O_ads_00)
        call run_proc_O_ads_00(cell)

    case(O_ads_01)
        call run_proc_O_ads_01(cell)

    end select

end subroutine run_proc_nr

end module proclist
