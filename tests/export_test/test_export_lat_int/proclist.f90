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
    call add_proc(nli_oxygen_diffus