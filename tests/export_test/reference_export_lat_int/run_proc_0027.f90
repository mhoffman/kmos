module run_proc_0027
use kind_values
use nli_0000
use nli_0001
use nli_0002
use nli_0003
use nli_0004
use nli_0005
use nli_0006
use nli_0007
use nli_0008
use nli_0009
use nli_0010
use nli_0011
use nli_0012
use nli_0013
use nli_0014
use nli_0015
use nli_0016
use nli_0017
use nli_0018
use nli_0019
use nli_0020
use nli_0021
use nli_0022
use nli_0023
use nli_0024
use nli_0025
use nli_0026
use nli_0027
use nli_0028
use nli_0029
use nli_0030
use nli_0031
use nli_0032
use nli_0033
use nli_0034
use nli_0035
use proclist_constants
implicit none
contains
subroutine run_proc_oxygen_diffusion_cus_cus_down(cell)

    integer(kind=iint), dimension(4), intent(in) :: cell

    ! disable processes that have to be disabled
    call del_proc(nli_co_adsorption_cus(cell + (/+0, -1, +0, 0/)), cell + (/+0, -1, +0, 1/))
    call del_proc(nli_co_adsorption_cus(cell + (/+0, +0, +0, 0/)), cell + (/+0, +0, +0, 1/))
    call del_proc(nli_co_desorption_cus(cell + (/+0, -1, +0, 0/)), cell + (/+0, -1, +0, 1/))
    call del_proc(nli_co_desorption_cus(cell + (/+0, +0, +0, 0/)), cell + (/+0, +0, +0, 1/))
    call del_proc(nli_co_diffusion_bridge_cus_left(cell + (/+1, -1, +0, 0/)), cell + (/+1, -1, +0, 1/))
    call del_proc(nli_co_diffusion_bridge_cus_left(cell + (/+1, +0, +0, 0/)), cell + (/+1, +0, +0, 1/))
    call del_proc(nli_co_diffusion_bridge_cus_right(cell + (/+0, -1, +0, 0/)), cell + (/+0, -1, +0, 1/))
    call del_proc(nli_co_diffusion_bridge_cus_right(cell + (/+0, +0, +0, 0/)), cell + (/+0, +0, +0, 1/))
    call del_proc(nli_co_diffusion_cus_bridge_left(cell + (/+0, -1, +0, 0/)), cell + (/+0, -1, +0, 1/))
    call del_proc(nli_co_diffusion_cus_bridge_left(cell + (/+0, +0, +0, 0/)), cell + (/+0, +0, +0, 1/))
    call del_proc(nli_co_diffusion_cus_bridge_right(cell + (/+0, -1, +0, 0/)), cell + (/+0, -1, +0, 1/))
    call del_proc(nli_co_diffusion_cus_bridge_right(cell + (/+0, +0, +0, 0/)), cell + (/+0, +0, +0, 1/))
    call del_proc(nli_co_diffusion_cus_cus_down(cell + (/+0, -1, +0, 0/)), cell + (/+0, -1, +0, 1/))
    call del_proc(nli_co_diffusion_cus_cus_down(cell + (/+0, +0, +0, 0/)), cell + (/+0, +0, +0, 1/))
    call del_proc(nli_co_diffusion_cus_cus_down(cell + (/+0, +1, +0, 0/)), cell + (/+0, +1, +0, 1/))
    call del_proc(nli_co_diffusion_cus_cus_up(cell + (/+0, -1, +0, 0/)), cell + (/+0, -1, +0, 1/))
    call del_proc(nli_co_diffusion_cus_cus_up(cell + (/+0, -2, +0, 0/)), cell + (/+0, -2, +0, 1/))
    call del_proc(nli_co_diffusion_cus_cus_up(cell + (/+0, +0, +0, 0/)), cell + (/+0, +0, +0, 1/))
    call del_proc(nli_oxygen_adsorption_bridge_cus_left(cell + (/+1, -1, +0, 0/)), cell + (/+1, -1, +0, 1/))
    call del_proc(nli_oxygen_adsorption_bridge_cus_left(cell + (/+1, +0, +0, 0/)), cell + (/+1, +0, +0, 1/))
    call del_proc(nli_oxygen_adsorption_bridge_cus_right(cell + (/+0, -1, +0, 0/)), cell + (/+0, -1, +0, 1/))
    call del_proc(nli_oxygen_adsorption_bridge_cus_right(cell + (/+0, +0, +0, 0/)), cell + (/+0, +0, +0, 1/))
    call del_proc(nli_oxygen_adsorption_cus_cus(cell + (/+0, -1, +0, 0/)), cell + (/+0, -1, +0, 1/))
    call del_proc(nli_oxygen_adsorption_cus_cus(cell + (/+0, -2, +0, 0/)), cell + (/+0, -2, +0, 1/))
    call del_proc(nli_oxygen_adsorption_cus_cus(cell + (/+0, +0, +0, 0/)), cell + (/+0, +0, +0, 1/))
    call del_proc(nli_oxygen_desorption_bridge_cus_left(cell + (/+1, -1, +0, 0/)), cell + (/+1, -1, +0, 1/))
    call del_proc(nli_oxygen_desorption_bridge_cus_left(cell + (/+1, +0, +0, 0/)), cell + (/+1, +0, +0, 1/))
    call del_proc(nli_oxygen_desorption_bridge_cus_right(cell + (/+0, -1, +0, 0/)), cell + (/+0, -1, +0, 1/))
    call del_proc(nli_oxygen_desorption_bridge_cus_right(cell + (/+0, +0, +0, 0/)), cell + (/+0, +0, +0, 1/))
    call del_proc(nli_oxygen_desorption_cus_cus(cell + (/+0, -1, +0, 0/)), cell + (/+0, -1, +0, 1/))
    call del_proc(nli_oxygen_desorption_cus_cus(cell + (/+0, -2, +0, 0/)), cell + (/+0, -2, +0, 1/))
    call del_proc(nli_oxygen_desorption_cus_cus(cell + (/+0, +0, +0, 0/)), cell + (/+0, +0, +0, 1/))
    call del_proc(nli_oxygen_diffusion_bridge_cus_left(cell + (/+1, -1, +0, 0/)), cell + (/+1, -1, +0, 1/))
    call del_proc(nli_oxygen_diffusion_bridge_cus_left(cell + (/+1, +0, +0, 0/)), cell + (/+1, +0, +0, 1/))
    call del_proc(nli_oxygen_diffusion_bridge_cus_right(cell + (/+0, -1, +0, 0/)), cell + (/+0, -1, +0, 1/))
    call del_proc(nli_oxygen_diffusion_bridge_cus_right(cell + (/+0, +0, +0, 0/)), cell + (/+0, +0, +0, 1/))
    call del_proc(nli_oxygen_diffusion_cus_bridge_left(cell + (/+0, -1, +0, 0/)), cell + (/+0, -1, +0, 1/))
    call del_proc(nli_oxygen_diffusion_cus_bridge_left(cell + (/+0, +0, +0, 0/)), cell + (/+0, +0, +0, 1/))
    call del_proc(nli_oxygen_diffusion_cus_bridge_right(cell + (/+0, -1, +0, 0/)), cell + (/+0, -1, +0, 1/))
    call del_proc(nli_oxygen_diffusion_cus_bridge_right(cell + (/+0, +0, +0, 0/)), cell + (/+0, +0, +0, 1/))
    call del_proc(nli_oxygen_diffusion_cus_cus_down(cell + (/+0, -1, +0, 0/)), cell + (/+0, -1, +0, 1/))
    call del_proc(nli_oxygen_diffusion_cus_cus_down(cell + (/+0, +0, +0, 0/)), cell + (/+0, +0, +0, 1/))
    call del_proc(nli_oxygen_diffusion_cus_cus_down(cell + (/+0, +1, +0, 0/)), cell + (/+0, +1, +0, 1/))
    call del_proc(nli_oxygen_diffusion_cus_cus_up(cell + (/+0, -1, +0, 0/)), cell + (/+0, -1, +0, 1/))
    call del_proc(nli_oxygen_diffusion_cus_cus_up(cell + (/+0, -2, +0, 0/)), cell + (/+0, -2, +0, 1/))
    call del_proc(nli_oxygen_diffusion_cus_cus_up(cell + (/+0, +0, +0, 0/)), cell + (/+0, +0, +0, 1/))
    call del_proc(nli_reaction_oxygen_bridge_co_cus_left(cell + (/+1, -1, +0, 0/)), cell + (/+1, -1, +0, 1/))
    call del_proc(nli_reaction_oxygen_bridge_co_cus_left(cell + (/+1, +0, +0, 0/)), cell + (/+1, +0, +0, 1/))
    call del_proc(nli_reaction_oxygen_bridge_co_cus_right(cell + (/+0, -1, +0, 0/)), cell + (/+0, -1, +0, 1/))
    call del_proc(nli_reaction_oxygen_bridge_co_cus_right(cell + (/+0, +0, +0, 0/)), cell + (/+0, +0, +0, 1/))
    call del_proc(nli_reaction_oxygen_cus_co_bridge_left(cell + (/+0, -1, +0, 0/)), cell + (/+0, -1, +0, 1/))
    call del_proc(nli_reaction_oxygen_cus_co_bridge_left(cell + (/+0, +0, +0, 0/)), cell + (/+0, +0, +0, 1/))
    call del_proc(nli_reaction_oxygen_cus_co_bridge_right(cell + (/+0, -1, +0, 0/)), cell + (/+0, -1, +0, 1/))
    call del_proc(nli_reaction_oxygen_cus_co_bridge_right(cell + (/+0, +0, +0, 0/)), cell + (/+0, +0, +0, 1/))
    call del_proc(nli_reaction_oxygen_cus_co_cus_down(cell + (/+0, -1, +0, 0/)), cell + (/+0, -1, +0, 1/))
    call del_proc(nli_reaction_oxygen_cus_co_cus_down(cell + (/+0, +0, +0, 0/)), cell + (/+0, +0, +0, 1/))
    call del_proc(nli_reaction_oxygen_cus_co_cus_down(cell + (/+0, +1, +0, 0/)), cell + (/+0, +1, +0, 1/))
    call del_proc(nli_reaction_oxygen_cus_co_cus_up(cell + (/+0, -1, +0, 0/)), cell + (/+0, -1, +0, 1/))
    call del_proc(nli_reaction_oxygen_cus_co_cus_up(cell + (/+0, -2, +0, 0/)), cell + (/+0, -2, +0, 1/))
    call del_proc(nli_reaction_oxygen_cus_co_cus_up(cell + (/+0, +0, +0, 0/)), cell + (/+0, +0, +0, 1/))

    ! update lattice
    call replace_species(cell + (/0, 0, 0, ruo2_cus/), oxygen, empty)
    call replace_species(cell + (/0, -1, 0, ruo2_cus/), empty, oxygen)

    ! enable processes that have to be enabled
    call add_proc(nli_co_adsorption_cus(cell + (/+0, -1, +0, 0/)), cell + (/+0, -1, +0, 1/))
    call add_proc(nli_co_adsorption_cus(cell + (/+0, +0, +0, 0/)), cell + (/+0, +0, +0, 1/))
    call add_proc(nli_co_desorption_cus(cell + (/+0, -1, +0, 0/)), cell + (/+0, -1, +0, 1/))
    call add_proc(nli_co_desorption_cus(cell + (/+0, +0, +0, 0/)), cell + (/+0, +0, +0, 1/))
    call add_proc(nli_co_diffusion_bridge_cus_left(cell + (/+1, -1, +0, 0/)), cell + (/+1, -1, +0, 1/))
    call add_proc(nli_co_diffusion_bridge_cus_left(cell + (/+1, +0, +0, 0/)), cell + (/+1, +0, +0, 1/))
    call add_proc(nli_co_diffusion_bridge_cus_right(cell + (/+0, -1, +0, 0/)), cell + (/+0, -1, +0, 1/))
    call add_proc(nli_co_diffusion_bridge_cus_right(cell + (/+0, +0, +0, 0/)), cell + (/+0, +0, +0, 1/))
    call add_proc(nli_co_diffusion_cus_bridge_left(cell + (/+0, -1, +0, 0/)), cell + (/+0, -1, +0, 1/))
    call add_proc(nli_co_diffusion_cus_bridge_left(cell + (/+0, +0, +0, 0/)), cell + (/+0, +0, +0, 1/))
    call add_proc(nli_co_diffusion_cus_bridge_right(cell + (/+0, -1, +0, 0/)), cell + (/+0, -1, +0, 1/))
    call add_proc(nli_co_diffusion_cus_bridge_right(cell + (/+0, +0, +0, 0/)), cell + (/+0, +0, +0, 1/))
    call add_proc(nli_co_diffusion_cus_cus_down(cell + (/+0, -1, +0, 0/)), cell + (/+0, -1, +0, 1/))
    call add_proc(nli_co_diffusion_cus_cus_down(cell + (/+0, +0, +0, 0/)), cell + (/+0, +0, +0, 1/))
    call add_proc(nli_co_diffusion_cus_cus_down(cell + (/+0, +1, +0, 0/)), cell + (/+0, +1, +0, 1/))
    call add_proc(nli_co_diffusion_cus_cus_up(cell + (/+0, -1, +0, 0/)), cell + (/+0, -1, +0, 1/))
    call add_proc(nli_co_diffusion_cus_cus_up(cell + (/+0, -2, +0, 0/)), cell + (/+0, -2, +0, 1/))
    call add_proc(nli_co_diffusion_cus_cus_up(cell + (/+0, +0, +0, 0/)), cell + (/+0, +0, +0, 1/))
    call add_proc(nli_oxygen_adsorption_bridge_cus_left(cell + (/+1, -1, +0, 0/)), cell + (/+1, -1, +0, 1/))
    call add_proc(nli_oxygen_adsorption_bridge_cus_left(cell + (/+1, +0, +0, 0/)), cell + (/+1, +0, +0, 1/))
    call add_proc(nli_oxygen_adsorption_bridge_cus_right(cell + (/+0, -1, +0, 0/)), cell + (/+0, -1, +0, 1/))
    call add_proc(nli_oxygen_adsorption_bridge_cus_right(cell + (/+0, +0, +0, 0/)), cell + (/+0, +0, +0, 1/))
    call add_proc(nli_oxygen_adsorption_cus_cus(cell + (/+0, -1, +0, 0/)), cell + (/+0, -1, +0, 1/))
    call add_proc(nli_oxygen_adsorption_cus_cus(cell + (/+0, -2, +0, 0/)), cell + (/+0, -2, +0, 1/))
    call add_proc(nli_oxygen_adsorption_cus_cus(cell + (/+0, +0, +0, 0/)), cell + (/+0, +0, +0, 1/))
    call add_proc(nli_oxygen_desorption_bridge_cus_left(cell + (/+1, -1, +0, 0/)), cell + (/+1, -1, +0, 1/))
    call add_proc(nli_oxygen_desorption_bridge_cus_left(cell + (/+1, +0, +0, 0/)), cell + (/+1, +0, +0, 1/))
    call add_proc(nli_oxygen_desorption_bridge_cus_right(cell + (/+0, -1, +0, 0/)), cell + (/+0, -1, +0, 1/))
    call add_proc(nli_oxygen_desorption_bridge_cus_right(cell + (/+0, +0, +0, 0/)), cell + (/+0, +0, +0, 1/))
    call add_proc(nli_oxygen_desorption_cus_cus(cell + (/+0, -1, +0, 0/)), cell + (/+0, -1, +0, 1/))
    call add_proc(nli_oxygen_desorption_cus_cus(cell + (/+0, -2, +0, 0/)), cell + (/+0, -2, +0, 1/))
    call add_proc(nli_oxygen_desorption_cus_cus(cell + (/+0, +0, +0, 0/)), cell + (/+0, +0, +0, 1/))
    call add_proc(nli_oxygen_diffusion_bridge_cus_left(cell + (/+1, -1, +0, 0/)), cell + (/+1, -1, +0, 1/))
    call add_proc(nli_oxygen_diffusion_bridge_cus_left(cell + (/+1, +0, +0, 0/)), cell + (/+1, +0, +0, 1/))
    call add_proc(nli_oxygen_diffusion_bridge_cus_right(cell + (/+0, -1, +0, 0/)), cell + (/+0, -1, +0, 1/))
    call add_proc(nli_oxygen_diffusion_bridge_cus_right(cell + (/+0, +0, +0, 0/)), cell + (/+0, +0, +0, 1/))
    call add_proc(nli_oxygen_diffusion_cus_bridge_left(cell + (/+0, -1, +0, 0/)), cell + (/+0, -1, +0, 1/))
    call add_proc(nli_oxygen_diffusion_cus_bridge_left(cell + (/+0, +0, +0, 0/)), cell + (/+0, +0, +0, 1/))
    call add_proc(nli_oxygen_diffusion_cus_bridge_right(cell + (/+0, -1, +0, 0/)), cell + (/+0, -1, +0, 1/))
    call add_proc(nli_oxygen_diffusion_cus_bridge_right(cell + (/+0, +0, +0, 0/)), cell + (/+0, +0, +0, 1/))
    call add_proc(nli_oxygen_diffusion_cus_cus_down(cell + (/+0, -1, +0, 0/)), cell + (/+0, -1, +0, 1/))
    call add_proc(nli_oxygen_diffusion_cus_cus_down(cell + (/+0, +0, +0, 0/)), cell + (/+0, +0, +0, 1/))
    call add_proc(nli_oxygen_diffusion_cus_cus_down(cell + (/+0, +1, +0, 0/)), cell + (/+0, +1, +0, 1/))
    call add_proc(nli_oxygen_diffusion_cus_cus_up(cell + (/+0, -1, +0, 0/)), cell + (/+0, -1, +0, 1/))
    call add_proc(nli_oxygen_diffusion_cus_cus_up(cell + (/+0, -2, +0, 0/)), cell + (/+0, -2, +0, 1/))
    call add_proc(nli_oxygen_diffusion_cus_cus_up(cell + (/+0, +0, +0, 0/)), cell + (/+0, +0, +0, 1/))
    call add_proc(nli_reaction_oxygen_bridge_co_cus_left(cell + (/+1, -1, +0, 0/)), cell + (/+1, -1, +0, 1/))
    call add_proc(nli_reaction_oxygen_bridge_co_cus_left(cell + (/+1, +0, +0, 0/)), cell + (/+1, +0, +0, 1/))
    call add_proc(nli_reaction_oxygen_bridge_co_cus_right(cell + (/+0, -1, +0, 0/)), cell + (/+0, -1, +0, 1/))
    call add_proc(nli_reaction_oxygen_bridge_co_cus_right(cell + (/+0, +0, +0, 0/)), cell + (/+0, +0, +0, 1/))
    call add_proc(nli_reaction_oxygen_cus_co_bridge_left(cell + (/+0, -1, +0, 0/)), cell + (/+0, -1, +0, 1/))
    call add_proc(nli_reaction_oxygen_cus_co_bridge_left(cell + (/+0, +0, +0, 0/)), cell + (/+0, +0, +0, 1/))
    call add_proc(nli_reaction_oxygen_cus_co_bridge_right(cell + (/+0, -1, +0, 0/)), cell + (/+0, -1, +0, 1/))
    call add_proc(nli_reaction_oxygen_cus_co_bridge_right(cell + (/+0, +0, +0, 0/)), cell + (/+0, +0, +0, 1/))
    call add_proc(nli_reaction_oxygen_cus_co_cus_down(cell + (/+0, -1, +0, 0/)), cell + (/+0, -1, +0, 1/))
    call add_proc(nli_reaction_oxygen_cus_co_cus_down(cell + (/+0, +0, +0, 0/)), cell + (/+0, +0, +0, 1/))
    call add_proc(nli_reaction_oxygen_cus_co_cus_down(cell + (/+0, +1, +0, 0/)), cell + (/+0, +1, +0, 1/))
    call add_proc(nli_reaction_oxygen_cus_co_cus_up(cell + (/+0, -1, +0, 0/)), cell + (/+0, -1, +0, 1/))
    call add_proc(nli_reaction_oxygen_cus_co_cus_up(cell + (/+0, -2, +0, 0/)), cell + (/+0, -2, +0, 1/))
    call add_proc(nli_reaction_oxygen_cus_co_cus_up(cell + (/+0, +0, +0, 0/)), cell + (/+0, +0, +0, 1/))

end subroutine run_proc_oxygen_diffusion_cus_cus_down

end module
