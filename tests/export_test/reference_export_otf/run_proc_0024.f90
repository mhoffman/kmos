module run_proc_0024

use kind_values
use lattice
use proclist_pars

implicit none
contains

subroutine run_proc_oxygen_diffusion_bridge_cus_rig0000(cell)

    integer(kind=iint), dimension(4), intent(in) :: cell


! Disable processes

    if(can_do(co_adsorption_cus,cell + (/ 0, 0, 0, 1/))) then
        call del_proc(co_adsorption_cus,cell + (/ 0, 0, 0, 1/))
    end if
    if(can_do(co_desorption_bridge,cell + (/ 0, 0, 0, 1/))) then
        call del_proc(co_desorption_bridge,cell + (/ 0, 0, 0, 1/))
    end if
    if(can_do(co_desorption_cus,cell + (/ 0, 0, 0, 1/))) then
        call del_proc(co_desorption_cus,cell + (/ 0, 0, 0, 1/))
    end if
    if(can_do(co_diffusion_bridge_bridge_down,cell + (/ 0, 0, 0, 1/))) then
        call del_proc(co_diffusion_bridge_bridge_down,cell + (/ 0, 0, 0, 1/))
    end if
    if(can_do(co_diffusion_bridge_bridge_up,cell + (/ 0, 0, 0, 1/))) then
        call del_proc(co_diffusion_bridge_bridge_up,cell + (/ 0, 0, 0, 1/))
    end if
    if(can_do(co_diffusion_bridge_cus_left,cell + (/ 1, 0, 0, 1/))) then
        call del_proc(co_diffusion_bridge_cus_left,cell + (/ 1, 0, 0, 1/))
    end if
    if(can_do(co_diffusion_bridge_cus_left,cell + (/ 0, 0, 0, 1/))) then
        call del_proc(co_diffusion_bridge_cus_left,cell + (/ 0, 0, 0, 1/))
    end if
    if(can_do(co_diffusion_bridge_cus_right,cell + (/ 0, 0, 0, 1/))) then
        call del_proc(co_diffusion_bridge_cus_right,cell + (/ 0, 0, 0, 1/))
    end if
    if(can_do(co_diffusion_cus_bridge_left,cell + (/ 0, 0, 0, 1/))) then
        call del_proc(co_diffusion_cus_bridge_left,cell + (/ 0, 0, 0, 1/))
    end if
    if(can_do(co_diffusion_cus_bridge_right,cell + (/ 0, 0, 0, 1/))) then
        call del_proc(co_diffusion_cus_bridge_right,cell + (/ 0, 0, 0, 1/))
    end if
    if(can_do(co_diffusion_cus_cus_down,cell + (/ 0, 1, 0, 1/))) then
        call del_proc(co_diffusion_cus_cus_down,cell + (/ 0, 1, 0, 1/))
    end if
    if(can_do(co_diffusion_cus_cus_down,cell + (/ 0, 0, 0, 1/))) then
        call del_proc(co_diffusion_cus_cus_down,cell + (/ 0, 0, 0, 1/))
    end if
    if(can_do(co_diffusion_cus_cus_up,cell + (/ 0, 0, 0, 1/))) then
        call del_proc(co_diffusion_cus_cus_up,cell + (/ 0, 0, 0, 1/))
    end if
    if(can_do(co_diffusion_cus_cus_up,cell + (/ 0, -1, 0, 1/))) then
        call del_proc(co_diffusion_cus_cus_up,cell + (/ 0, -1, 0, 1/))
    end if
    if(can_do(oxygen_adsorption_bridge_cus_le0000,cell + (/ 1, 0, 0, 1/))) then
        call del_proc(oxygen_adsorption_bridge_cus_le0000,cell + (/ 1, 0, 0, 1/))
    end if
    if(can_do(oxygen_adsorption_bridge_cus_ri0000,cell + (/ 0, 0, 0, 1/))) then
        call del_proc(oxygen_adsorption_bridge_cus_ri0000,cell + (/ 0, 0, 0, 1/))
    end if
    if(can_do(oxygen_adsorption_cus_cus,cell + (/ 0, 0, 0, 1/))) then
        call del_proc(oxygen_adsorption_cus_cus,cell + (/ 0, 0, 0, 1/))
    end if
    if(can_do(oxygen_adsorption_cus_cus,cell + (/ 0, -1, 0, 1/))) then
        call del_proc(oxygen_adsorption_cus_cus,cell + (/ 0, -1, 0, 1/))
    end if
    if(can_do(oxygen_desorption_bridge_bridge,cell + (/ 0, 0, 0, 1/))) then
        call del_proc(oxygen_desorption_bridge_bridge,cell + (/ 0, 0, 0, 1/))
    end if
    if(can_do(oxygen_desorption_bridge_bridge,cell + (/ 0, -1, 0, 1/))) then
        call del_proc(oxygen_desorption_bridge_bridge,cell + (/ 0, -1, 0, 1/))
    end if
    if(can_do(oxygen_desorption_bridge_cus_le0000,cell + (/ 0, 0, 0, 1/))) then
        call del_proc(oxygen_desorption_bridge_cus_le0000,cell + (/ 0, 0, 0, 1/))
    end if
    if(can_do(oxygen_desorption_bridge_cus_ri0000,cell + (/ 0, 0, 0, 1/))) then
        call del_proc(oxygen_desorption_bridge_cus_ri0000,cell + (/ 0, 0, 0, 1/))
    end if
    if(can_do(oxygen_diffusion_bridge_bridge_0000,cell + (/ 0, 0, 0, 1/))) then
        call del_proc(oxygen_diffusion_bridge_bridge_0000,cell + (/ 0, 0, 0, 1/))
    end if
    if(can_do(oxygen_diffusion_bridge_bridge_0001,cell + (/ 0, 0, 0, 1/))) then
        call del_proc(oxygen_diffusion_bridge_bridge_0001,cell + (/ 0, 0, 0, 1/))
    end if
    if(can_do(oxygen_diffusion_bridge_cus_lef0000,cell + (/ 1, 0, 0, 1/))) then
        call del_proc(oxygen_diffusion_bridge_cus_lef0000,cell + (/ 1, 0, 0, 1/))
    end if
    if(can_do(oxygen_diffusion_bridge_cus_lef0000,cell + (/ 0, 0, 0, 1/))) then
        call del_proc(oxygen_diffusion_bridge_cus_lef0000,cell + (/ 0, 0, 0, 1/))
    end if
    if(can_do(oxygen_diffusion_bridge_cus_rig0000,cell + (/ 0, 0, 0, 1/))) then
        call del_proc(oxygen_diffusion_bridge_cus_rig0000,cell + (/ 0, 0, 0, 1/))
    end if
    if(can_do(oxygen_diffusion_cus_cus_down,cell + (/ 0, 1, 0, 1/))) then
        call del_proc(oxygen_diffusion_cus_cus_down,cell + (/ 0, 1, 0, 1/))
    end if
    if(can_do(oxygen_diffusion_cus_cus_up,cell + (/ 0, -1, 0, 1/))) then
        call del_proc(oxygen_diffusion_cus_cus_up,cell + (/ 0, -1, 0, 1/))
    end if
    if(can_do(reaction_oxygen_bridge_co_bridg0000,cell + (/ 0, 1, 0, 1/))) then
        call del_proc(reaction_oxygen_bridge_co_bridg0000,cell + (/ 0, 1, 0, 1/))
    end if
    if(can_do(reaction_oxygen_bridge_co_bridg0000,cell + (/ 0, 0, 0, 1/))) then
        call del_proc(reaction_oxygen_bridge_co_bridg0000,cell + (/ 0, 0, 0, 1/))
    end if
    if(can_do(reaction_oxygen_bridge_co_bridg0001,cell + (/ 0, 0, 0, 1/))) then
        call del_proc(reaction_oxygen_bridge_co_bridg0001,cell + (/ 0, 0, 0, 1/))
    end if
    if(can_do(reaction_oxygen_bridge_co_bridg0001,cell + (/ 0, -1, 0, 1/))) then
        call del_proc(reaction_oxygen_bridge_co_bridg0001,cell + (/ 0, -1, 0, 1/))
    end if
    if(can_do(reaction_oxygen_bridge_co_cus_l0000,cell + (/ 1, 0, 0, 1/))) then
        call del_proc(reaction_oxygen_bridge_co_cus_l0000,cell + (/ 1, 0, 0, 1/))
    end if
    if(can_do(reaction_oxygen_bridge_co_cus_l0000,cell + (/ 0, 0, 0, 1/))) then
        call del_proc(reaction_oxygen_bridge_co_cus_l0000,cell + (/ 0, 0, 0, 1/))
    end if
    if(can_do(reaction_oxygen_bridge_co_cus_r0000,cell + (/ 0, 0, 0, 1/))) then
        call del_proc(reaction_oxygen_bridge_co_cus_r0000,cell + (/ 0, 0, 0, 1/))
    end if
    if(can_do(reaction_oxygen_cus_co_bridge_l0000,cell + (/ 0, 0, 0, 1/))) then
        call del_proc(reaction_oxygen_cus_co_bridge_l0000,cell + (/ 0, 0, 0, 1/))
    end if
    if(can_do(reaction_oxygen_cus_co_bridge_r0000,cell + (/ -1, 0, 0, 1/))) then
        call del_proc(reaction_oxygen_cus_co_bridge_r0000,cell + (/ -1, 0, 0, 1/))
    end if
    if(can_do(reaction_oxygen_cus_co_cus_down,cell + (/ 0, 1, 0, 1/))) then
        call del_proc(reaction_oxygen_cus_co_cus_down,cell + (/ 0, 1, 0, 1/))
    end if
    if(can_do(reaction_oxygen_cus_co_cus_up,cell + (/ 0, -1, 0, 1/))) then
        call del_proc(reaction_oxygen_cus_co_cus_up,cell + (/ 0, -1, 0, 1/))
    end if

! Update the lattice
    call replace_species(cell + (/0, 0, 0, ruo2_bridge/),oxygen,empty)
    call replace_species(cell + (/0, 0, 0, ruo2_cus/),empty,oxygen)

! Update rate constants


! Enable processes

    call add_proc(co_adsorption_bridge, cell + (/ 0, 0, 0, 1/), gr_co_adsorption_bridge(cell + (/ 0, 0, 0, 0/)))
    call add_proc(oxygen_diffusion_cus_bridge_lef0000, cell + (/ 0, 0, 0, 1/), gr_oxygen_diffusion_cus_bridge_lef0000(cell + (/ 0, 0, 0, 0/)))
    select case(get_species(cell + (/0, 1, 0, ruo2_bridge/)))
    case(co)
        call add_proc(co_diffusion_bridge_bridge_down, cell + (/ 0, 1, 0, 1/), gr_co_diffusion_bridge_bridge_down(cell + (/ 0, 1, 0, 0/)))
    case(oxygen)
        call add_proc(oxygen_diffusion_bridge_bridge_0000, cell + (/ 0, 1, 0, 1/), gr_oxygen_diffusion_bridge_bridge_0000(cell + (/ 0, 1, 0, 0/)))
    case(empty)
        call add_proc(oxygen_adsorption_bridge_bridge, cell + (/ 0, 0, 0, 1/), gr_oxygen_adsorption_bridge_bridge(cell + (/ 0, 0, 0, 0/)))
    end select

    select case(get_species(cell + (/0, -1, 0, ruo2_bridge/)))
    case(co)
        call add_proc(co_diffusion_bridge_bridge_up, cell + (/ 0, -1, 0, 1/), gr_co_diffusion_bridge_bridge_up(cell + (/ 0, -1, 0, 0/)))
    case(oxygen)
        call add_proc(oxygen_diffusion_bridge_bridge_0001, cell + (/ 0, -1, 0, 1/), gr_oxygen_diffusion_bridge_bridge_0001(cell + (/ 0, -1, 0, 0/)))
    case(empty)
        call add_proc(oxygen_adsorption_bridge_bridge, cell + (/ 0, -1, 0, 1/), gr_oxygen_adsorption_bridge_bridge(cell + (/ 0, -1, 0, 0/)))
    end select

    select case(get_species(cell + (/-1, 0, 0, ruo2_cus/)))
    case(co)
        call add_proc(co_diffusion_cus_bridge_right, cell + (/ -1, 0, 0, 1/), gr_co_diffusion_cus_bridge_right(cell + (/ -1, 0, 0, 0/)))
    case(oxygen)
        call add_proc(oxygen_diffusion_cus_bridge_rig0000, cell + (/ -1, 0, 0, 1/), gr_oxygen_diffusion_cus_bridge_rig0000(cell + (/ -1, 0, 0, 0/)))
    case(empty)
        call add_proc(oxygen_adsorption_bridge_cus_le0000, cell + (/ 0, 0, 0, 1/), gr_oxygen_adsorption_bridge_cus_le0000(cell + (/ 0, 0, 0, 0/)))
    end select

    select case(get_species(cell + (/1, 0, 0, ruo2_bridge/)))
    case(co)
        call add_proc(reaction_oxygen_cus_co_bridge_r0000, cell + (/ 0, 0, 0, 1/), gr_reaction_oxygen_cus_co_bridge_r0000(cell + (/ 0, 0, 0, 0/)))
    case(empty)
        call add_proc(oxygen_diffusion_cus_bridge_rig0000, cell + (/ 0, 0, 0, 1/), gr_oxygen_diffusion_cus_bridge_rig0000(cell + (/ 0, 0, 0, 0/)))
    case(oxygen)
        call add_proc(oxygen_desorption_bridge_cus_le0000, cell + (/ 1, 0, 0, 1/), gr_oxygen_desorption_bridge_cus_le0000(cell + (/ 1, 0, 0, 0/)))
    end select

    select case(get_species(cell + (/0, 1, 0, ruo2_cus/)))
    case(co)
        call add_proc(reaction_oxygen_cus_co_cus_up, cell + (/ 0, 0, 0, 1/), gr_reaction_oxygen_cus_co_cus_up(cell + (/ 0, 0, 0, 0/)))
    case(empty)
        call add_proc(oxygen_diffusion_cus_cus_up, cell + (/ 0, 0, 0, 1/), gr_oxygen_diffusion_cus_cus_up(cell + (/ 0, 0, 0, 0/)))
    case(oxygen)
        call add_proc(oxygen_desorption_cus_cus, cell + (/ 0, 0, 0, 1/), gr_oxygen_desorption_cus_cus(cell + (/ 0, 0, 0, 0/)))
    end select

    select case(get_species(cell + (/0, -1, 0, ruo2_cus/)))
    case(co)
        call add_proc(reaction_oxygen_cus_co_cus_down, cell + (/ 0, 0, 0, 1/), gr_reaction_oxygen_cus_co_cus_down(cell + (/ 0, 0, 0, 0/)))
    case(empty)
        call add_proc(oxygen_diffusion_cus_cus_down, cell + (/ 0, 0, 0, 1/), gr_oxygen_diffusion_cus_cus_down(cell + (/ 0, 0, 0, 0/)))
    case(oxygen)
        call add_proc(oxygen_desorption_cus_cus, cell + (/ 0, -1, 0, 1/), gr_oxygen_desorption_cus_cus(cell + (/ 0, -1, 0, 0/)))
    end select


end subroutine run_proc_oxygen_diffusion_bridge_cus_rig0000

end module run_proc_0024
