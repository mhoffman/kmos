module proclist
use kind_values
use base, only: &
    update_accum_rate, &
    update_integ_rate, &
    determine_procsite, &
    update_clocks, &
    avail_sites, &
    set_null_species, &
    increment_procstat

use lattice, only: &
    Pd100, &
    PdO, &
    Pd100_h1, &
    Pd100_h2, &
    Pd100_h4, &
    Pd100_h5, &
    Pd100_b1, &
    Pd100_b2, &
    Pd100_b3, &
    Pd100_b4, &
    Pd100_b5, &
    Pd100_b6, &
    Pd100_b7, &
    Pd100_b8, &
    Pd100_b9, &
    Pd100_b10, &
    Pd100_h3, &
    PdO_bridge2, &
    PdO_hollow1, &
    PdO_hollow2, &
    PdO_bridge1, &
    PdO_Pd2, &
    PdO_Pd3, &
    PdO_Pd4, &
    PdO_hollow3, &
    PdO_hollow4, &
    PdO_Pd1, &
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
use run_proc_0036; use nli_0036
use run_proc_0037; use nli_0037
use run_proc_0038; use nli_0038
use run_proc_0039; use nli_0039
use run_proc_0040; use nli_0040
use run_proc_0041; use nli_0041
use run_proc_0042; use nli_0042
use run_proc_0043; use nli_0043
use run_proc_0044; use nli_0044
use run_proc_0045; use nli_0045

implicit none
integer(kind=iint), parameter, public :: representation_length = 31
integer(kind=iint), public :: seed_size = 12
integer(kind=iint), public :: seed ! random seed
integer(kind=iint), public, dimension(:), allocatable :: seed_arr ! random seed


integer(kind=iint), parameter, public :: nr_of_proc = 46

character(len=7), parameter, public :: backend = "lat_int"

contains

subroutine run_proc_nr(proc, nr_cell)
    integer(kind=iint), intent(in) :: nr_cell
    integer(kind=iint), intent(in) :: proc

    integer(kind=iint), dimension(4) :: cell

    cell = nr2lattice(nr_cell, :) + (/0, 0, 0, -1/)
    call increment_procstat(proc)

    select case(proc)
    case(destruct9)
        call run_proc_destruct9(cell)
    case(destruct8)
        call run_proc_destruct8(cell)
    case(o_COdif_h1h2up)
        call run_proc_o_COdif_h1h2up(cell)
    case(destruct3)
        call run_proc_destruct3(cell)
    case(destruct2)
        call run_proc_destruct2(cell)
    case(destruct1)
        call run_proc_destruct1(cell)
    case(destruct7)
        call run_proc_destruct7(cell)
    case(destruct6)
        call run_proc_destruct6(cell)
    case(destruct5)
        call run_proc_destruct5(cell)
    case(destruct4)
        call run_proc_destruct4(cell)
    case(m_COads_b10)
        call run_proc_m_COads_b10(cell)
    case(m_COdes_b9)
        call run_proc_m_COdes_b9(cell)
    case(m_COdes_b8)
        call run_proc_m_COdes_b8(cell)
    case(o_COads_hollow2)
        call run_proc_o_COads_hollow2(cell)
    case(m_COdes_b5)
        call run_proc_m_COdes_b5(cell)
    case(m_COdes_b4)
        call run_proc_m_COdes_b4(cell)
    case(m_COdes_b7)
        call run_proc_m_COdes_b7(cell)
    case(m_COdes_b6)
        call run_proc_m_COdes_b6(cell)
    case(m_COdes_b1)
        call run_proc_m_COdes_b1(cell)
    case(o_COads_hollow1)
        call run_proc_o_COads_hollow1(cell)
    case(m_COdes_b3)
        call run_proc_m_COdes_b3(cell)
    case(m_COdes_b2)
        call run_proc_m_COdes_b2(cell)
    case(m_COads_b3)
        call run_proc_m_COads_b3(cell)
    case(m_COads_b2)
        call run_proc_m_COads_b2(cell)
    case(m_COads_b1)
        call run_proc_m_COads_b1(cell)
    case(m_COads_b7)
        call run_proc_m_COads_b7(cell)
    case(m_COads_b6)
        call run_proc_m_COads_b6(cell)
    case(m_COads_b5)
        call run_proc_m_COads_b5(cell)
    case(m_COads_b4)
        call run_proc_m_COads_b4(cell)
    case(m_COads_b9)
        call run_proc_m_COads_b9(cell)
    case(m_COads_b8)
        call run_proc_m_COads_b8(cell)
    case(o_COdes_bridge2)
        call run_proc_o_COdes_bridge2(cell)
    case(o_COdes_bridge1)
        call run_proc_o_COdes_bridge1(cell)
    case(o_COdif_h1h2down)
        call run_proc_o_COdif_h1h2down(cell)
    case(o_O2des_h2h1)
        call run_proc_o_O2des_h2h1(cell)
    case(o_COdes_hollow1)
        call run_proc_o_COdes_hollow1(cell)
    case(o_COdes_hollow2)
        call run_proc_o_COdes_hollow2(cell)
    case(o_O2des_h1h2)
        call run_proc_o_O2des_h1h2(cell)
    case(destruct11)
        call run_proc_destruct11(cell)
    case(destruct10)
        call run_proc_destruct10(cell)
    case(oxidize1)
        call run_proc_oxidize1(cell)
    case(o_O2ads_h2h1)
        call run_proc_o_O2ads_h2h1(cell)
    case(o_COads_bridge1)
        call run_proc_o_COads_bridge1(cell)
    case(m_COdes_b10)
        call run_proc_m_COdes_b10(cell)
    case(o_COads_bridge2)
        call run_proc_o_COads_bridge2(cell)
    case(o_O2ads_h1h2)
        call run_proc_o_O2ads_h1h2(cell)
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

    call add_proc(nli_destruct9(cell), site)
    call add_proc(nli_destruct8(cell), site)
    call add_proc(nli_o_COdif_h1h2up(cell), site)
    call add_proc(nli_destruct3(cell), site)
    call add_proc(nli_destruct2(cell), site)
    call add_proc(nli_destruct1(cell), site)
    call add_proc(nli_destruct7(cell), site)
    call add_proc(nli_destruct6(cell), site)
    call add_proc(nli_destruct5(cell), site)
    call add_proc(nli_destruct4(cell), site)
    call add_proc(nli_m_COads_b10(cell), site)
    call add_proc(nli_m_COdes_b9(cell), site)
    call add_proc(nli_m_COdes_b8(cell), site)
    call add_proc(nli_o_COads_hollow2(cell), site)
    call add_proc(nli_m_COdes_b5(cell), site)
    call add_proc(nli_m_COdes_b4(cell), site)
    call add_proc(nli_m_COdes_b7(cell), site)
    call add_proc(nli_m_COdes_b6(cell), site)
    call add_proc(nli_m_COdes_b1(cell), site)
    call add_proc(nli_o_COads_hollow1(cell), site)
    call add_proc(nli_m_COdes_b3(cell), site)
    call add_proc(nli_m_COdes_b2(cell), site)
    call add_proc(nli_m_COads_b3(cell), site)
    call add_proc(nli_m_COads_b2(cell), site)
    call add_proc(nli_m_COads_b1(cell), site)
    call add_proc(nli_m_COads_b7(cell), site)
    call add_proc(nli_m_COads_b6(cell), site)
    call add_proc(nli_m_COads_b5(cell), site)
    call add_proc(nli_m_COads_b4(cell), site)
    call add_proc(nli_m_COads_b9(cell), site)
    call add_proc(nli_m_COads_b8(cell), site)
    call add_proc(nli_o_COdes_bridge2(cell), site)
    call add_proc(nli_o_COdes_bridge1(cell), site)
    call add_proc(nli_o_COdif_h1h2down(cell), site)
    call add_proc(nli_o_O2des_h2h1(cell), site)
    call add_proc(nli_o_COdes_hollow1(cell), site)
    call add_proc(nli_o_COdes_hollow2(cell), site)
    call add_proc(nli_o_O2des_h1h2(cell), site)
    call add_proc(nli_destruct11(cell), site)
    call add_proc(nli_destruct10(cell), site)
    call add_proc(nli_oxidize1(cell), site)
    call add_proc(nli_o_O2ads_h2h1(cell), site)
    call add_proc(nli_o_COads_bridge1(cell), site)
    call add_proc(nli_m_COdes_b10(cell), site)
    call add_proc(nli_o_COads_bridge2(cell), site)
    call add_proc(nli_o_O2ads_h1h2(cell), site)
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
    integer(kind=iint), intent(in) :: n

    real(kind=rsingle) :: ran_proc, ran_time, ran_site
    integer(kind=iint) :: nr_site, proc_nr, i

    do i = 1, n
    call random_number(ran_time)
    call random_number(ran_proc)
    call random_number(ran_site)
    call update_accum_rate
    call update_clocks(ran_time)

    call update_integ_rate
    call determine_procsite(ran_proc, ran_time, proc_nr, nr_site)
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
    call determine_procsite(ran_proc, ran_time, proc_nr, nr_site)
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
    ! nr_of_species = 5, spuck = 25
    real(kind=rdouble), dimension(0:3, 1:25), intent(out) :: occupation

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

subroutine init(input_system_size, system_name, layer, no_banner)

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
    integer(kind=iint), intent(in) :: layer
    integer(kind=iint), dimension(2), intent(in) :: input_system_size

    character(len=400), intent(in) :: system_name

    logical, optional, intent(in) :: no_banner

    if (.not. no_banner) then
        print *, "+------------------------------------------------------------+"
        print *, "|                                                            |"
        print *, "| This kMC Model 'sqrt5PdO' was written by                   |"
        print *, "|                                                            |"
        print *, "|          Max J. Hoffmann (max.hoffmann@ch.tum.de)          |"
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
        print *, "| I appreciate, but do not require, attribution.             |"
        print *, "| An attribution usually includes the program name           |"
        print *, "| author, and URL. For example:                              |"
        print *, "| kmos by Max J. Hoffmann, (http://mhoffman.github.com/kmos) |"
        print *, "|                                                            |"
        print *, "+------------------------------------------------------------+"
        print *, ""
        print *, ""
    endif
    call set_null_species(null_species)
    call allocate_system(nr_of_proc, input_system_size, system_name)
    call initialize_state(layer)
end subroutine init

subroutine initialize_state(layer)

!****f* proclist/initialize_state
! FUNCTION
!    Initialize all sites and book-keeping array
!    for the given layer.
!
! ARGUMENTS
!
!    * ``layer`` integer representing layer
!******
    integer(kind=iint), intent(in) :: layer

    integer(kind=iint) :: i, j, k, nr
    ! initialize random number generator
    allocate(seed_arr(seed_size))
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
                case (Pd100)
                    call replace_species((/i, j, k, Pd100_h1/), null_species, default_species)
                    call replace_species((/i, j, k, Pd100_h2/), null_species, default_species)
                    call replace_species((/i, j, k, Pd100_h4/), null_species, default_species)
                    call replace_species((/i, j, k, Pd100_h5/), null_species, default_species)
                    call replace_species((/i, j, k, Pd100_b1/), null_species, default_species)
                    call replace_species((/i, j, k, Pd100_b2/), null_species, default_species)
                    call replace_species((/i, j, k, Pd100_b3/), null_species, default_species)
                    call replace_species((/i, j, k, Pd100_b4/), null_species, default_species)
                    call replace_species((/i, j, k, Pd100_b5/), null_species, default_species)
                    call replace_species((/i, j, k, Pd100_b6/), null_species, default_species)
                    call replace_species((/i, j, k, Pd100_b7/), null_species, default_species)
                    call replace_species((/i, j, k, Pd100_b8/), null_species, default_species)
                    call replace_species((/i, j, k, Pd100_b9/), null_species, default_species)
                    call replace_species((/i, j, k, Pd100_b10/), null_species, default_species)
                    call replace_species((/i, j, k, Pd100_h3/), null_species, default_species)
                case (PdO)
                    call replace_species((/i, j, k, PdO_bridge2/), null_species, empty)
                    call replace_species((/i, j, k, PdO_hollow1/), null_species, empty)
                    call replace_species((/i, j, k, PdO_hollow2/), null_species, empty)
                    call replace_species((/i, j, k, PdO_bridge1/), null_species, empty)
                    call replace_species((/i, j, k, PdO_Pd2/), null_species, Pd)
                    call replace_species((/i, j, k, PdO_Pd3/), null_species, Pd)
                    call replace_species((/i, j, k, PdO_Pd4/), null_species, Pd)
                    call replace_species((/i, j, k, PdO_hollow3/), null_species, oxygen)
                    call replace_species((/i, j, k, PdO_hollow4/), null_species, oxygen)
                    call replace_species((/i, j, k, PdO_Pd1/), null_species, Pd)
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
