module run_proc_0005

use kind_values
use lattice, only: &
    ruo2_bridge, &
    ruo2_cus, &
    can_do, &
    del_proc, &
    add_proc, &
    replace_species, &
    get_species
use proclist_constants, only: &
    co, &
    empty, &
    oxygen, &
    co_adsorption_bridge, &
    co_adsorption_cus, &
    co_desorption_bridge, &
    co_desorption_cus, &
    co_diffusion_bridge_bridge_down, &
    co_diffusion_bridge_bridge_up, &
    co_diffusion_bridge_cus_left, &
    co_diffusion_bridge_cus_right, &
    co_diffusion_cus_bridge_left, &
    co_diffusion_cus_bridge_right, &
    co_diffusion_cus_cus_down, &
    co_diffusion_cus_cus_up, &
    oxygen_adsorption_bridge_bridge, &
    oxygen_adsorption_bridge_cus_le0000, &
    oxygen_adsorption_bridge_cus_ri0000, &
    oxygen_adsorption_cus_cus, &
    oxygen_desorption_bridge_bridge, &
    oxygen_desorption_bridge_cus_le0000, &
    oxygen_desorption_bridge_cus_ri0000, &
    oxygen_desorption_cus_cus, &
    oxygen_diffusion_bridge_bridge_0000, &
    oxygen_diffusion_bridge_bridge_0001, &
    oxygen_diffusion_bridge_cus_lef0000, &
    oxygen_diffusion_bridge_cus_rig0000, &
    oxygen_diffusion_cus_bridge_lef0000, &
    oxygen_diffusion_cus_bridge_rig0000, &
    oxygen_diffusion_cus_cus_down, &
    oxygen_diffusion_cus_cus_up, &
    reaction_oxygen_bridge_co_bridg0000, &
    reaction_oxygen_bridge_co_bridg0001, &
    reaction_oxygen_bridge_co_cus_l0000, &
    reaction_oxygen_bridge_co_cus_r0000, &
    reaction_oxygen_cus_co_bridge_l0000, &
    reaction_oxygen_cus_co_bridge_r0000, &
    reaction_oxygen_cus_co_cus_down, &
    reaction_oxygen_cus_co_cus_up
use proclist_pars, only: &
    gr_co_adsorption_bridge, &
    gr_co_adsorption_cus, &
    gr_co_desorption_bridge, &
    gr_co_desorption_cus, &
    gr_co_diffusion_bridge_bridge_down, &
    gr_co_diffusion_bridge_bridge_up, &
    gr_co_diffusion_bridge_cus_left, &
    gr_co_diffusion_bridge_cus_right, &
    gr_co_diffusion_cus_bridge_left, &
    gr_co_diffusion_cus_bridge_right, &
    gr_co_diffusion_cus_cus_down, &
    gr_co_diffusion_cus_cus_up, &
    gr_oxygen_adsorption_bridge_bridge, &
    gr_oxygen_adsorption_bridge_cus_le0000, &
    gr_oxygen_adsorption_bridge_cus_ri0000, &
    gr_oxygen_adsorption_cus_cus, &
    gr_oxygen_desorption_bridge_bridge, &
    gr_oxygen_desorption_bridge_cus_le0000, &
    gr_oxygen_desorption_bridge_cus_ri0000, &
    gr_oxygen_desorption_cus_cus, &
    gr_oxygen_diffusion_bridge_bridge_0000, &
    gr_oxygen_diffusion_bridge_bridge_0001, &
    gr_oxygen_diffusion_bridge_cus_lef0000, &
    gr_oxygen_diffusion_bridge_cus_rig0000, &
    gr_oxygen_diffusion_cus_bridge_lef0000, &
    gr_oxygen_diffusion_cus_bridge_rig0000, &
    gr_oxygen_diffusion_cus_cus_down, &
    gr_oxygen_diffusion_cus_cus_up, &
    gr_reaction_oxygen_bridge_co_bridg0000, &
    gr_reaction_oxygen_bridge_co_bridg0001, &
    gr_reaction_oxygen_bridge_co_cus_l0000, &
    gr_reaction_oxygen_bridge_co_cus_r0000, &
    gr_reaction_oxygen_cus_co_bridge_l0000, &
    gr_reaction_oxygen_cus_co_bridge_r0000, &
    gr_reaction_oxygen_cus_co_cus_down, &
    gr_reaction_oxygen_cus_co_cus_up

implicit none
contains

subroutine run_proc_co_diffusion_bridge_bridge_down(cell)

    integer(kind=iint), dimension(4), intent(in) :: cell


! Disable processes

    if(can_do(co_adsorption_bridge,cell + (/ 0, -1, 0, 1/))) then
        call del_proc(co_adsorption_bridge,cell + (/ 0, -1, 0, 1/))
    end if
    if(can_do(co_desorption_bridge,cell + (/ 0, 0, 0, 1/))) then
        call del_proc(co_desorption_bridge,cell + (/ 0, 0, 0, 1/))
    end if
    if(can_do(co_diffusion_bridge_bridge_down,cell + (/ 0, 0, 0, 1/))) then
        call del_proc(co_diffusion_bridge_bridge_down,cell + (/ 0, 0, 0, 1/))
    end if
    if(can_do(co_diffusion_bridge_bridge_up,cell + (/ 0, 0, 0, 1/))) then
        call del_proc(co_diffusion_bridge_bridge_up,cell + (/ 0, 0, 0, 1/))
    end if
    if(can_do(co_diffusion_bridge_bridge_up,cell + (/ 0, -2, 0, 1/))) then
        call del_proc(co_diffusion_bridge_bridge_up,cell + (/ 0, -2, 0, 1/))
    end if
    if(can_do(co_diffusion_bridge_cus_left,cell + (/ 0, 0, 0, 1/))) then
        call del_proc(co_diffusion_bridge_cus_left,cell + (/ 0, 0, 0, 1/))
    end if
    if(can_do(co_diffusion_bridge_cus_right,cell + (/ 0, 0, 0, 1/))) then
        call del_proc(co_diffusion_bridge_cus_right,cell + (/ 0, 0, 0, 1/))
    end if
    if(can_do(co_diffusion_cus_bridge_left,cell + (/ 0, -1, 0, 1/))) then
        call del_proc(co_diffusion_cus_bridge_left,cell + (/ 0, -1, 0, 1/))
    end if
    if(can_do(co_diffusion_cus_bridge_right,cell + (/ -1, -1, 0, 1/))) then
        call del_proc(co_diffusion_cus_bridge_right,cell + (/ -1, -1, 0, 1/))
    end if
    if(can_do(oxygen_adsorption_bridge_bridge,cell + (/ 0, -2, 0, 1/))) then
        call del_proc(oxygen_adsorption_bridge_bridge,cell + (/ 0, -2, 0, 1/))
    end if
    if(can_do(oxygen_adsorption_bridge_bridge,cell + (/ 0, -1, 0, 1/))) then
        call del_proc(oxygen_adsorption_bridge_bridge,cell + (/ 0, -1, 0, 1/))
    end if
    if(can_do(oxygen_adsorption_bridge_cus_le0000,cell + (/ 0, -1, 0, 1/))) then
        call del_proc(oxygen_adsorption_bridge_cus_le0000,cell + (/ 0, -1, 0, 1/))
    end if
    if(can_do(oxygen_adsorption_bridge_cus_ri0000,cell + (/ 0, -1, 0, 1/))) then
        call del_proc(oxygen_adsorption_bridge_cus_ri0000,cell + (/ 0, -1, 0, 1/))
    end if
    if(can_do(oxygen_desorption_bridge_bridge,cell + (/ 0, -2, 0, 1/))) then
        call del_proc(oxygen_desorption_bridge_bridge,cell + (/ 0, -2, 0, 1/))
    end if
    if(can_do(oxygen_desorption_bridge_bridge,cell + (/ 0, -1, 0, 1/))) then
        call del_proc(oxygen_desorption_bridge_bridge,cell + (/ 0, -1, 0, 1/))
    end if
    if(can_do(oxygen_desorption_bridge_bridge,cell + (/ 0, 0, 0, 1/))) then
        call del_proc(oxygen_desorption_bridge_bridge,cell + (/ 0, 0, 0, 1/))
    end if
    if(can_do(oxygen_desorption_bridge_cus_le0000,cell + (/ 0, 0, 0, 1/))) then
        call del_proc(oxygen_desorption_bridge_cus_le0000,cell + (/ 0, 0, 0, 1/))
    end if
    if(can_do(oxygen_desorption_bridge_cus_le0000,cell + (/ 0, -1, 0, 1/))) then
        call del_proc(oxygen_desorption_bridge_cus_le0000,cell + (/ 0, -1, 0, 1/))
    end if
    if(can_do(oxygen_desorption_bridge_cus_ri0000,cell + (/ 0, 0, 0, 1/))) then
        call del_proc(oxygen_desorption_bridge_cus_ri0000,cell + (/ 0, 0, 0, 1/))
    end if
    if(can_do(oxygen_desorption_bridge_cus_ri0000,cell + (/ 0, -1, 0, 1/))) then
        call del_proc(oxygen_desorption_bridge_cus_ri0000,cell + (/ 0, -1, 0, 1/))
    end if
    if(can_do(oxygen_diffusion_bridge_bridge_0000,cell + (/ 0, 0, 0, 1/))) then
        call del_proc(oxygen_diffusion_bridge_bridge_0000,cell + (/ 0, 0, 0, 1/))
    end if
    if(can_do(oxygen_diffusion_bridge_bridge_0000,cell + (/ 0, -1, 0, 1/))) then
        call del_proc(oxygen_diffusion_bridge_bridge_0000,cell + (/ 0, -1, 0, 1/))
    end if
    if(can_do(oxygen_diffusion_bridge_bridge_0001,cell + (/ 0, -2, 0, 1/))) then
        call del_proc(oxygen_diffusion_bridge_bridge_0001,cell + (/ 0, -2, 0, 1/))
    end if
    if(can_do(oxygen_diffusion_bridge_bridge_0001,cell + (/ 0, -1, 0, 1/))) then
        call del_proc(oxygen_diffusion_bridge_bridge_0001,cell + (/ 0, -1, 0, 1/))
    end if
    if(can_do(oxygen_diffusion_bridge_bridge_0001,cell + (/ 0, 0, 0, 1/))) then
        call del_proc(oxygen_diffusion_bridge_bridge_0001,cell + (/ 0, 0, 0, 1/))
    end if
    if(can_do(oxygen_diffusion_bridge_cus_lef0000,cell + (/ 0, 0, 0, 1/))) then
        call del_proc(oxygen_diffusion_bridge_cus_lef0000,cell + (/ 0, 0, 0, 1/))
    end if
    if(can_do(oxygen_diffusion_bridge_cus_lef0000,cell + (/ 0, -1, 0, 1/))) then
        call del_proc(oxygen_diffusion_bridge_cus_lef0000,cell + (/ 0, -1, 0, 1/))
    end if
    if(can_do(oxygen_diffusion_bridge_cus_rig0000,cell + (/ 0, 0, 0, 1/))) then
        call del_proc(oxygen_diffusion_bridge_cus_rig0000,cell + (/ 0, 0, 0, 1/))
    end if
    if(can_do(oxygen_diffusion_bridge_cus_rig0000,cell + (/ 0, -1, 0, 1/))) then
        call del_proc(oxygen_diffusion_bridge_cus_rig0000,cell + (/ 0, -1, 0, 1/))
    end if
    if(can_do(oxygen_diffusion_cus_bridge_lef0000,cell + (/ 0, -1, 0, 1/))) then
        call del_proc(oxygen_diffusion_cus_bridge_lef0000,cell + (/ 0, -1, 0, 1/))
    end if
    if(can_do(oxygen_diffusion_cus_bridge_rig0000,cell + (/ -1, -1, 0, 1/))) then
        call del_proc(oxygen_diffusion_cus_bridge_rig0000,cell + (/ -1, -1, 0, 1/))
    end if
    if(can_do(reaction_oxygen_bridge_co_bridg0000,cell + (/ 0, 0, 0, 1/))) then
        call del_proc(reaction_oxygen_bridge_co_bridg0000,cell + (/ 0, 0, 0, 1/))
    end if
    if(can_do(reaction_oxygen_bridge_co_bridg0000,cell + (/ 0, -1, 0, 1/))) then
        call del_proc(reaction_oxygen_bridge_co_bridg0000,cell + (/ 0, -1, 0, 1/))
    end if
    if(can_do(reaction_oxygen_bridge_co_bridg0000,cell + (/ 0, 1, 0, 1/))) then
        call del_proc(reaction_oxygen_bridge_co_bridg0000,cell + (/ 0, 1, 0, 1/))
    end if
    if(can_do(reaction_oxygen_bridge_co_bridg0001,cell + (/ 0, 0, 0, 1/))) then
        call del_proc(reaction_oxygen_bridge_co_bridg0001,cell + (/ 0, 0, 0, 1/))
    end if
    if(can_do(reaction_oxygen_bridge_co_bridg0001,cell + (/ 0, -1, 0, 1/))) then
        call del_proc(reaction_oxygen_bridge_co_bridg0001,cell + (/ 0, -1, 0, 1/))
    end if
    if(can_do(reaction_oxygen_bridge_co_cus_l0000,cell + (/ 0, 0, 0, 1/))) then
        call del_proc(reaction_oxygen_bridge_co_cus_l0000,cell + (/ 0, 0, 0, 1/))
    end if
    if(can_do(reaction_oxygen_bridge_co_cus_l0000,cell + (/ 0, -1, 0, 1/))) then
        call del_proc(reaction_oxygen_bridge_co_cus_l0000,cell + (/ 0, -1, 0, 1/))
    end if
    if(can_do(reaction_oxygen_bridge_co_cus_r0000,cell + (/ 0, 0, 0, 1/))) then
        call del_proc(reaction_oxygen_bridge_co_cus_r0000,cell + (/ 0, 0, 0, 1/))
    end if
    if(can_do(reaction_oxygen_bridge_co_cus_r0000,cell + (/ 0, -1, 0, 1/))) then
        call del_proc(reaction_oxygen_bridge_co_cus_r0000,cell + (/ 0, -1, 0, 1/))
    end if
    if(can_do(reaction_oxygen_cus_co_bridge_l0000,cell + (/ 0, 0, 0, 1/))) then
        call del_proc(reaction_oxygen_cus_co_bridge_l0000,cell + (/ 0, 0, 0, 1/))
    end if
    if(can_do(reaction_oxygen_cus_co_bridge_r0000,cell + (/ -1, 0, 0, 1/))) then
        call del_proc(reaction_oxygen_cus_co_bridge_r0000,cell + (/ -1, 0, 0, 1/))
    end if

! Update the lattice
    call replace_species(cell + (/0, -1, 0, ruo2_bridge/),empty,co)
    call replace_species(cell + (/0, 0, 0, ruo2_bridge/),co,empty)

! Update rate constants


! Enable processes

    call add_proc(co_adsorption_bridge, cell + (/ 0, 0, 0, 1/), gr_co_adsorption_bridge(cell + (/ 0, 0, 0, 0/)))
    call add_proc(co_desorption_bridge, cell + (/ 0, -1, 0, 1/), gr_co_desorption_bridge(cell + (/ 0, -1, 0, 0/)))
    call add_proc(co_diffusion_bridge_bridge_up, cell + (/ 0, -1, 0, 1/), gr_co_diffusion_bridge_bridge_up(cell + (/ 0, -1, 0, 0/)))
    select case(get_species(cell + (/0, 1, 0, ruo2_bridge/)))
    case(co)
        call add_proc(co_diffusion_bridge_bridge_down, cell + (/ 0, 1, 0, 1/), gr_co_diffusion_bridge_bridge_down(cell + (/ 0, 1, 0, 0/)))
    case(empty)
        call add_proc(oxygen_adsorption_bridge_bridge, cell + (/ 0, 0, 0, 1/), gr_oxygen_adsorption_bridge_bridge(cell + (/ 0, 0, 0, 0/)))
    case(oxygen)
        call add_proc(oxygen_diffusion_bridge_bridge_0000, cell + (/ 0, 1, 0, 1/), gr_oxygen_diffusion_bridge_bridge_0000(cell + (/ 0, 1, 0, 0/)))
    end select

    select case(get_species(cell + (/0, 0, 0, ruo2_cus/)))
    case(co)
        call add_proc(co_diffusion_cus_bridge_left, cell + (/ 0, 0, 0, 1/), gr_co_diffusion_cus_bridge_left(cell + (/ 0, 0, 0, 0/)))
    case(empty)
        call add_proc(oxygen_adsorption_bridge_cus_ri0000, cell + (/ 0, 0, 0, 1/), gr_oxygen_adsorption_bridge_cus_ri0000(cell + (/ 0, 0, 0, 0/)))
    case(oxygen)
        call add_proc(oxygen_diffusion_cus_bridge_lef0000, cell + (/ 0, 0, 0, 1/), gr_oxygen_diffusion_cus_bridge_lef0000(cell + (/ 0, 0, 0, 0/)))
    end select

    select case(get_species(cell + (/-1, 0, 0, ruo2_cus/)))
    case(co)
        call add_proc(co_diffusion_cus_bridge_right, cell + (/ -1, 0, 0, 1/), gr_co_diffusion_cus_bridge_right(cell + (/ -1, 0, 0, 0/)))
    case(empty)
        call add_proc(oxygen_adsorption_bridge_cus_le0000, cell + (/ 0, 0, 0, 1/), gr_oxygen_adsorption_bridge_cus_le0000(cell + (/ 0, 0, 0, 0/)))
    case(oxygen)
        call add_proc(oxygen_diffusion_cus_bridge_rig0000, cell + (/ -1, 0, 0, 1/), gr_oxygen_diffusion_cus_bridge_rig0000(cell + (/ -1, 0, 0, 0/)))
    end select

    select case(get_species(cell + (/0, -2, 0, ruo2_bridge/)))
    case(empty)
        call add_proc(co_diffusion_bridge_bridge_down, cell + (/ 0, -1, 0, 1/), gr_co_diffusion_bridge_bridge_down(cell + (/ 0, -1, 0, 0/)))
    case(oxygen)
        call add_proc(reaction_oxygen_bridge_co_bridg0001, cell + (/ 0, -2, 0, 1/), gr_reaction_oxygen_bridge_co_bridg0001(cell + (/ 0, -2, 0, 0/)))
    end select

    select case(get_species(cell + (/-1, -1, 0, ruo2_cus/)))
    case(empty)
        call add_proc(co_diffusion_bridge_cus_left, cell + (/ 0, -1, 0, 1/), gr_co_diffusion_bridge_cus_left(cell + (/ 0, -1, 0, 0/)))
    case(oxygen)
        call add_proc(reaction_oxygen_cus_co_bridge_r0000, cell + (/ -1, -1, 0, 1/), gr_reaction_oxygen_cus_co_bridge_r0000(cell + (/ -1, -1, 0, 0/)))
    end select

    select case(get_species(cell + (/0, -1, 0, ruo2_cus/)))
    case(empty)
        call add_proc(co_diffusion_bridge_cus_right, cell + (/ 0, -1, 0, 1/), gr_co_diffusion_bridge_cus_right(cell + (/ 0, -1, 0, 0/)))
    case(oxygen)
        call add_proc(reaction_oxygen_cus_co_bridge_l0000, cell + (/ 0, -1, 0, 1/), gr_reaction_oxygen_cus_co_bridge_l0000(cell + (/ 0, -1, 0, 0/)))
    end select


end subroutine run_proc_co_diffusion_bridge_bridge_down

end module run_proc_0005
