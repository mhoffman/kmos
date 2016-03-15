module run_proc_0010

use kind_values
use lattice
use proclist_pars

implicit none
contains

subroutine run_proc_CO_diff_hollow_bridge_r(cell)

    integer(kind=iint), dimension(4), intent(in) :: cell


! Disable processes

    if(can_do(CO_ads_bridge,cell + (/ 1, 0, 0, 1/))) then
        call del_proc(CO_ads_bridge,cell + (/ 1, 0, 0, 1/))
    end if
    if(can_do(CO_des_hollow,cell + (/ 0, 0, 0, 1/))) then
        call del_proc(CO_des_hollow,cell + (/ 0, 0, 0, 1/))
    end if
    if(can_do(CO_diff_bridge_bridge_l,cell + (/ 2, 0, 0, 1/))) then
        call del_proc(CO_diff_bridge_bridge_l,cell + (/ 2, 0, 0, 1/))
    end if
    if(can_do(CO_diff_bridge_bridge_r,cell + (/ 0, 0, 0, 1/))) then
        call del_proc(CO_diff_bridge_bridge_r,cell + (/ 0, 0, 0, 1/))
    end if
    if(can_do(CO_diff_hollow_bridge,cell + (/ 1, 0, 0, 1/))) then
        call del_proc(CO_diff_hollow_bridge,cell + (/ 1, 0, 0, 1/))
    end if
    if(can_do(CO_diff_hollow_bridge,cell + (/ 0, 0, 0, 1/))) then
        call del_proc(CO_diff_hollow_bridge,cell + (/ 0, 0, 0, 1/))
    end if
    if(can_do(CO_diff_hollow_bridge_r,cell + (/ 0, 0, 0, 1/))) then
        call del_proc(CO_diff_hollow_bridge_r,cell + (/ 0, 0, 0, 1/))
    end if
    if(can_do(CO_diff_hollow_hollow_l,cell + (/ 0, 0, 0, 1/))) then
        call del_proc(CO_diff_hollow_hollow_l,cell + (/ 0, 0, 0, 1/))
    end if
    if(can_do(CO_diff_hollow_hollow_r,cell + (/ 0, 0, 0, 1/))) then
        call del_proc(CO_diff_hollow_hollow_r,cell + (/ 0, 0, 0, 1/))
    end if
    if(can_do(CO_oxi_bridge_bridge_l,cell + (/ 1, 0, 0, 1/))) then
        call del_proc(CO_oxi_bridge_bridge_l,cell + (/ 1, 0, 0, 1/))
    end if
    if(can_do(CO_oxi_bridge_bridge_r,cell + (/ 1, 0, 0, 1/))) then
        call del_proc(CO_oxi_bridge_bridge_r,cell + (/ 1, 0, 0, 1/))
    end if
    if(can_do(CO_oxi_bridge_hollow,cell + (/ 1, 0, 0, 1/))) then
        call del_proc(CO_oxi_bridge_hollow,cell + (/ 1, 0, 0, 1/))
    end if
    if(can_do(CO_oxi_bridge_hollow,cell + (/ 0, 0, 0, 1/))) then
        call del_proc(CO_oxi_bridge_hollow,cell + (/ 0, 0, 0, 1/))
    end if
    if(can_do(CO_oxi_bridge_hollow_l,cell + (/ 1, 0, 0, 1/))) then
        call del_proc(CO_oxi_bridge_hollow_l,cell + (/ 1, 0, 0, 1/))
    end if
    if(can_do(CO_oxi_hollow_bridge,cell + (/ 0, 0, 0, 1/))) then
        call del_proc(CO_oxi_hollow_bridge,cell + (/ 0, 0, 0, 1/))
    end if
    if(can_do(CO_oxi_hollow_bridge_r,cell + (/ 0, 0, 0, 1/))) then
        call del_proc(CO_oxi_hollow_bridge_r,cell + (/ 0, 0, 0, 1/))
    end if
    if(can_do(CO_oxi_hollow_hollow_l,cell + (/ 1, 0, 0, 1/))) then
        call del_proc(CO_oxi_hollow_hollow_l,cell + (/ 1, 0, 0, 1/))
    end if
    if(can_do(CO_oxi_hollow_hollow_l,cell + (/ 0, 0, 0, 1/))) then
        call del_proc(CO_oxi_hollow_hollow_l,cell + (/ 0, 0, 0, 1/))
    end if
    if(can_do(CO_oxi_hollow_hollow_r,cell + (/ -1, 0, 0, 1/))) then
        call del_proc(CO_oxi_hollow_hollow_r,cell + (/ -1, 0, 0, 1/))
    end if
    if(can_do(CO_oxi_hollow_hollow_r,cell + (/ 0, 0, 0, 1/))) then
        call del_proc(CO_oxi_hollow_hollow_r,cell + (/ 0, 0, 0, 1/))
    end if
    if(can_do(O2_ads_bridge_bridge,cell + (/ 1, 0, 0, 1/))) then
        call del_proc(O2_ads_bridge_bridge,cell + (/ 1, 0, 0, 1/))
    end if
    if(can_do(O2_ads_bridge_bridge,cell + (/ 0, 0, 0, 1/))) then
        call del_proc(O2_ads_bridge_bridge,cell + (/ 0, 0, 0, 1/))
    end if
    if(can_do(O2_ads_bridge_hollow,cell + (/ 1, 0, 0, 1/))) then
        call del_proc(O2_ads_bridge_hollow,cell + (/ 1, 0, 0, 1/))
    end if
    if(can_do(O2_ads_hollow_bridge,cell + (/ 0, 0, 0, 1/))) then
        call del_proc(O2_ads_hollow_bridge,cell + (/ 0, 0, 0, 1/))
    end if
    if(can_do(O2_des_bridge_bridge_r,cell + (/ 1, 0, 0, 1/))) then
        call del_proc(O2_des_bridge_bridge_r,cell + (/ 1, 0, 0, 1/))
    end if
    if(can_do(O2_des_bridge_bridge_r,cell + (/ 0, 0, 0, 1/))) then
        call del_proc(O2_des_bridge_bridge_r,cell + (/ 0, 0, 0, 1/))
    end if
    if(can_do(O2_des_bridge_hollow,cell + (/ 1, 0, 0, 1/))) then
        call del_proc(O2_des_bridge_hollow,cell + (/ 1, 0, 0, 1/))
    end if
    if(can_do(O2_des_bridge_hollow,cell + (/ 0, 0, 0, 1/))) then
        call del_proc(O2_des_bridge_hollow,cell + (/ 0, 0, 0, 1/))
    end if
    if(can_do(O2_des_hollow_bridge_r,cell + (/ 0, 0, 0, 1/))) then
        call del_proc(O2_des_hollow_bridge_r,cell + (/ 0, 0, 0, 1/))
    end if
    if(can_do(O2_des_hollow_hollow_r,cell + (/ -1, 0, 0, 1/))) then
        call del_proc(O2_des_hollow_hollow_r,cell + (/ -1, 0, 0, 1/))
    end if
    if(can_do(O2_des_hollow_hollow_r,cell + (/ 0, 0, 0, 1/))) then
        call del_proc(O2_des_hollow_hollow_r,cell + (/ 0, 0, 0, 1/))
    end if
    if(can_do(O_diff_bridge_bridge_l,cell + (/ 1, 0, 0, 1/))) then
        call del_proc(O_diff_bridge_bridge_l,cell + (/ 1, 0, 0, 1/))
    end if
    if(can_do(O_diff_bridge_bridge_l,cell + (/ 2, 0, 0, 1/))) then
        call del_proc(O_diff_bridge_bridge_l,cell + (/ 2, 0, 0, 1/))
    end if
    if(can_do(O_diff_bridge_bridge_r,cell + (/ 1, 0, 0, 1/))) then
        call del_proc(O_diff_bridge_bridge_r,cell + (/ 1, 0, 0, 1/))
    end if
    if(can_do(O_diff_bridge_bridge_r,cell + (/ 0, 0, 0, 1/))) then
        call del_proc(O_diff_bridge_bridge_r,cell + (/ 0, 0, 0, 1/))
    end if
    if(can_do(O_diff_bridge_hollow,cell + (/ 1, 0, 0, 1/))) then
        call del_proc(O_diff_bridge_hollow,cell + (/ 1, 0, 0, 1/))
    end if
    if(can_do(O_diff_bridge_hollow_l,cell + (/ 1, 0, 0, 1/))) then
        call del_proc(O_diff_bridge_hollow_l,cell + (/ 1, 0, 0, 1/))
    end if
    if(can_do(O_diff_hollow_bridge,cell + (/ 1, 0, 0, 1/))) then
        call del_proc(O_diff_hollow_bridge,cell + (/ 1, 0, 0, 1/))
    end if
    if(can_do(O_diff_hollow_bridge,cell + (/ 0, 0, 0, 1/))) then
        call del_proc(O_diff_hollow_bridge,cell + (/ 0, 0, 0, 1/))
    end if
    if(can_do(O_diff_hollow_bridge_r,cell + (/ 0, 0, 0, 1/))) then
        call del_proc(O_diff_hollow_bridge_r,cell + (/ 0, 0, 0, 1/))
    end if
    if(can_do(O_diff_hollow_hollow_l,cell + (/ 0, 0, 0, 1/))) then
        call del_proc(O_diff_hollow_hollow_l,cell + (/ 0, 0, 0, 1/))
    end if
    if(can_do(O_diff_hollow_hollow_r,cell + (/ 0, 0, 0, 1/))) then
        call del_proc(O_diff_hollow_hollow_r,cell + (/ 0, 0, 0, 1/))
    end if

! Update the lattice
    call replace_species(cell + (/0, 0, 0, pdo_hollow/),CO,empty)
    call replace_species(cell + (/1, 0, 0, pdo_bridge/),empty,CO)

! Update rate constants

    if(can_do(CO_des_bridge,cell + (/ 1, 0, 0, 1/))) then
        call update_rates_matrix(CO_des_bridge,cell + (/ 1, 0, 0, 1/),gr_CO_des_bridge(cell + (/ 1, 0, 0, 0/)))
    end if
    if(can_do(CO_des_bridge,cell + (/ 0, 0, 0, 1/))) then
        call update_rates_matrix(CO_des_bridge,cell + (/ 0, 0, 0, 1/),gr_CO_des_bridge(cell + (/ 0, 0, 0, 0/)))
    end if
    if(can_do(CO_des_bridge,cell + (/ 2, 0, 0, 1/))) then
        call update_rates_matrix(CO_des_bridge,cell + (/ 2, 0, 0, 1/),gr_CO_des_bridge(cell + (/ 2, 0, 0, 0/)))
    end if
    if(can_do(CO_des_hollow,cell + (/ 1, 0, 0, 1/))) then
        call update_rates_matrix(CO_des_hollow,cell + (/ 1, 0, 0, 1/),gr_CO_des_hollow(cell + (/ 1, 0, 0, 0/)))
    end if
    if(can_do(CO_des_hollow,cell + (/ -1, 0, 0, 1/))) then
        call update_rates_matrix(CO_des_hollow,cell + (/ -1, 0, 0, 1/),gr_CO_des_hollow(cell + (/ -1, 0, 0, 0/)))
    end if
    if(can_do(CO_diff_bridge_bridge_l,cell + (/ 3, 0, 0, 1/))) then
        call update_rates_matrix(CO_diff_bridge_bridge_l,cell + (/ 3, 0, 0, 1/),gr_CO_diff_bridge_bridge_l(cell + (/ 3, 0, 0, 0/)))
    end if
    if(can_do(CO_diff_bridge_bridge_l,cell + (/ 0, 0, 0, 1/))) then
        call update_rates_matrix(CO_diff_bridge_bridge_l,cell + (/ 0, 0, 0, 1/),gr_CO_diff_bridge_bridge_l(cell + (/ 0, 0, 0, 0/)))
    end if
    if(can_do(CO_diff_bridge_bridge_r,cell + (/ 1, 0, 0, 1/))) then
        call update_rates_matrix(CO_diff_bridge_bridge_r,cell + (/ 1, 0, 0, 1/),gr_CO_diff_bridge_bridge_r(cell + (/ 1, 0, 0, 0/)))
    end if
    if(can_do(CO_diff_bridge_bridge_r,cell + (/ -1, 0, 0, 1/))) then
        call update_rates_matrix(CO_diff_bridge_bridge_r,cell + (/ -1, 0, 0, 1/),gr_CO_diff_bridge_bridge_r(cell + (/ -1, 0, 0, 0/)))
    end if
    if(can_do(CO_diff_bridge_bridge_r,cell + (/ 2, 0, 0, 1/))) then
        call update_rates_matrix(CO_diff_bridge_bridge_r,cell + (/ 2, 0, 0, 1/),gr_CO_diff_bridge_bridge_r(cell + (/ 2, 0, 0, 0/)))
    end if
    if(can_do(CO_diff_bridge_hollow,cell + (/ 1, 0, 0, 1/))) then
        call update_rates_matrix(CO_diff_bridge_hollow,cell + (/ 1, 0, 0, 1/),gr_CO_diff_bridge_hollow(cell + (/ 1, 0, 0, 0/)))
    end if
    if(can_do(CO_diff_bridge_hollow,cell + (/ -1, 0, 0, 1/))) then
        call update_rates_matrix(CO_diff_bridge_hollow,cell + (/ -1, 0, 0, 1/),gr_CO_diff_bridge_hollow(cell + (/ -1, 0, 0, 0/)))
    end if
    if(can_do(CO_diff_bridge_hollow,cell + (/ 0, 0, 0, 1/))) then
        call update_rates_matrix(CO_diff_bridge_hollow,cell + (/ 0, 0, 0, 1/),gr_CO_diff_bridge_hollow(cell + (/ 0, 0, 0, 0/)))
    end if
    if(can_do(CO_diff_bridge_hollow,cell + (/ 2, 0, 0, 1/))) then
        call update_rates_matrix(CO_diff_bridge_hollow,cell + (/ 2, 0, 0, 1/),gr_CO_diff_bridge_hollow(cell + (/ 2, 0, 0, 0/)))
    end if
    if(can_do(CO_diff_bridge_hollow_l,cell + (/ 0, 0, 0, 1/))) then
        call update_rates_matrix(CO_diff_bridge_hollow_l,cell + (/ 0, 0, 0, 1/),gr_CO_diff_bridge_hollow_l(cell + (/ 0, 0, 0, 0/)))
    end if
    if(can_do(CO_diff_bridge_hollow_l,cell + (/ 2, 0, 0, 1/))) then
        call update_rates_matrix(CO_diff_bridge_hollow_l,cell + (/ 2, 0, 0, 1/),gr_CO_diff_bridge_hollow_l(cell + (/ 2, 0, 0, 0/)))
    end if
    if(can_do(CO_diff_hollow_bridge,cell + (/ -1, 0, 0, 1/))) then
        call update_rates_matrix(CO_diff_hollow_bridge,cell + (/ -1, 0, 0, 1/),gr_CO_diff_hollow_bridge(cell + (/ -1, 0, 0, 0/)))
    end if
    if(can_do(CO_diff_hollow_bridge,cell + (/ 2, 0, 0, 1/))) then
        call update_rates_matrix(CO_diff_hollow_bridge,cell + (/ 2, 0, 0, 1/),gr_CO_diff_hollow_bridge(cell + (/ 2, 0, 0, 0/)))
    end if
    if(can_do(CO_diff_hollow_bridge_r,cell + (/ 1, 0, 0, 1/))) then
        call update_rates_matrix(CO_diff_hollow_bridge_r,cell + (/ 1, 0, 0, 1/),gr_CO_diff_hollow_bridge_r(cell + (/ 1, 0, 0, 0/)))
    end if
    if(can_do(CO_diff_hollow_bridge_r,cell + (/ -1, 0, 0, 1/))) then
        call update_rates_matrix(CO_diff_hollow_bridge_r,cell + (/ -1, 0, 0, 1/),gr_CO_diff_hollow_bridge_r(cell + (/ -1, 0, 0, 0/)))
    end if
    if(can_do(CO_diff_hollow_hollow_l,cell + (/ -1, 0, 0, 1/))) then
        call update_rates_matrix(CO_diff_hollow_hollow_l,cell + (/ -1, 0, 0, 1/),gr_CO_diff_hollow_hollow_l(cell + (/ -1, 0, 0, 0/)))
    end if
    if(can_do(CO_diff_hollow_hollow_l,cell + (/ 2, 0, 0, 1/))) then
        call update_rates_matrix(CO_diff_hollow_hollow_l,cell + (/ 2, 0, 0, 1/),gr_CO_diff_hollow_hollow_l(cell + (/ 2, 0, 0, 0/)))
    end if
    if(can_do(CO_diff_hollow_hollow_r,cell + (/ 1, 0, 0, 1/))) then
        call update_rates_matrix(CO_diff_hollow_hollow_r,cell + (/ 1, 0, 0, 1/),gr_CO_diff_hollow_hollow_r(cell + (/ 1, 0, 0, 0/)))
    end if
    if(can_do(CO_diff_hollow_hollow_r,cell + (/ -2, 0, 0, 1/))) then
        call update_rates_matrix(CO_diff_hollow_hollow_r,cell + (/ -2, 0, 0, 1/),gr_CO_diff_hollow_hollow_r(cell + (/ -2, 0, 0, 0/)))
    end if
    if(can_do(CO_diff_hollow_hollow_r,cell + (/ -1, 0, 0, 1/))) then
        call update_rates_matrix(CO_diff_hollow_hollow_r,cell + (/ -1, 0, 0, 1/),gr_CO_diff_hollow_hollow_r(cell + (/ -1, 0, 0, 0/)))
    end if
    if(can_do(O2_des_bridge_bridge_r,cell + (/ -1, 0, 0, 1/))) then
        call update_rates_matrix(O2_des_bridge_bridge_r,cell + (/ -1, 0, 0, 1/),gr_O2_des_bridge_bridge_r(cell + (/ -1, 0, 0, 0/)))
    end if
    if(can_do(O2_des_bridge_bridge_r,cell + (/ 2, 0, 0, 1/))) then
        call update_rates_matrix(O2_des_bridge_bridge_r,cell + (/ 2, 0, 0, 1/),gr_O2_des_bridge_bridge_r(cell + (/ 2, 0, 0, 0/)))
    end if
    if(can_do(O2_des_bridge_hollow,cell + (/ -1, 0, 0, 1/))) then
        call update_rates_matrix(O2_des_bridge_hollow,cell + (/ -1, 0, 0, 1/),gr_O2_des_bridge_hollow(cell + (/ -1, 0, 0, 0/)))
    end if
    if(can_do(O2_des_bridge_hollow,cell + (/ 2, 0, 0, 1/))) then
        call update_rates_matrix(O2_des_bridge_hollow,cell + (/ 2, 0, 0, 1/),gr_O2_des_bridge_hollow(cell + (/ 2, 0, 0, 0/)))
    end if
    if(can_do(O2_des_hollow_bridge_r,cell + (/ 1, 0, 0, 1/))) then
        call update_rates_matrix(O2_des_hollow_bridge_r,cell + (/ 1, 0, 0, 1/),gr_O2_des_hollow_bridge_r(cell + (/ 1, 0, 0, 0/)))
    end if
    if(can_do(O2_des_hollow_bridge_r,cell + (/ -1, 0, 0, 1/))) then
        call update_rates_matrix(O2_des_hollow_bridge_r,cell + (/ -1, 0, 0, 1/),gr_O2_des_hollow_bridge_r(cell + (/ -1, 0, 0, 0/)))
    end if
    if(can_do(O2_des_hollow_hollow_r,cell + (/ 1, 0, 0, 1/))) then
        call update_rates_matrix(O2_des_hollow_hollow_r,cell + (/ 1, 0, 0, 1/),gr_O2_des_hollow_hollow_r(cell + (/ 1, 0, 0, 0/)))
    end if
    if(can_do(O2_des_hollow_hollow_r,cell + (/ -2, 0, 0, 1/))) then
        call update_rates_matrix(O2_des_hollow_hollow_r,cell + (/ -2, 0, 0, 1/),gr_O2_des_hollow_hollow_r(cell + (/ -2, 0, 0, 0/)))
    end if
    if(can_do(O_diff_bridge_bridge_l,cell + (/ 3, 0, 0, 1/))) then
        call update_rates_matrix(O_diff_bridge_bridge_l,cell + (/ 3, 0, 0, 1/),gr_O_diff_bridge_bridge_l(cell + (/ 3, 0, 0, 0/)))
    end if
    if(can_do(O_diff_bridge_bridge_l,cell + (/ 0, 0, 0, 1/))) then
        call update_rates_matrix(O_diff_bridge_bridge_l,cell + (/ 0, 0, 0, 1/),gr_O_diff_bridge_bridge_l(cell + (/ 0, 0, 0, 0/)))
    end if
    if(can_do(O_diff_bridge_bridge_r,cell + (/ -1, 0, 0, 1/))) then
        call update_rates_matrix(O_diff_bridge_bridge_r,cell + (/ -1, 0, 0, 1/),gr_O_diff_bridge_bridge_r(cell + (/ -1, 0, 0, 0/)))
    end if
    if(can_do(O_diff_bridge_bridge_r,cell + (/ 2, 0, 0, 1/))) then
        call update_rates_matrix(O_diff_bridge_bridge_r,cell + (/ 2, 0, 0, 1/),gr_O_diff_bridge_bridge_r(cell + (/ 2, 0, 0, 0/)))
    end if
    if(can_do(O_diff_bridge_hollow,cell + (/ -1, 0, 0, 1/))) then
        call update_rates_matrix(O_diff_bridge_hollow,cell + (/ -1, 0, 0, 1/),gr_O_diff_bridge_hollow(cell + (/ -1, 0, 0, 0/)))
    end if
    if(can_do(O_diff_bridge_hollow,cell + (/ 0, 0, 0, 1/))) then
        call update_rates_matrix(O_diff_bridge_hollow,cell + (/ 0, 0, 0, 1/),gr_O_diff_bridge_hollow(cell + (/ 0, 0, 0, 0/)))
    end if
    if(can_do(O_diff_bridge_hollow,cell + (/ 2, 0, 0, 1/))) then
        call update_rates_matrix(O_diff_bridge_hollow,cell + (/ 2, 0, 0, 1/),gr_O_diff_bridge_hollow(cell + (/ 2, 0, 0, 0/)))
    end if
    if(can_do(O_diff_bridge_hollow_l,cell + (/ 0, 0, 0, 1/))) then
        call update_rates_matrix(O_diff_bridge_hollow_l,cell + (/ 0, 0, 0, 1/),gr_O_diff_bridge_hollow_l(cell + (/ 0, 0, 0, 0/)))
    end if
    if(can_do(O_diff_bridge_hollow_l,cell + (/ 2, 0, 0, 1/))) then
        call update_rates_matrix(O_diff_bridge_hollow_l,cell + (/ 2, 0, 0, 1/),gr_O_diff_bridge_hollow_l(cell + (/ 2, 0, 0, 0/)))
    end if
    if(can_do(O_diff_hollow_bridge,cell + (/ -1, 0, 0, 1/))) then
        call update_rates_matrix(O_diff_hollow_bridge,cell + (/ -1, 0, 0, 1/),gr_O_diff_hollow_bridge(cell + (/ -1, 0, 0, 0/)))
    end if
    if(can_do(O_diff_hollow_bridge,cell + (/ 2, 0, 0, 1/))) then
        call update_rates_matrix(O_diff_hollow_bridge,cell + (/ 2, 0, 0, 1/),gr_O_diff_hollow_bridge(cell + (/ 2, 0, 0, 0/)))
    end if
    if(can_do(O_diff_hollow_bridge_r,cell + (/ 1, 0, 0, 1/))) then
        call update_rates_matrix(O_diff_hollow_bridge_r,cell + (/ 1, 0, 0, 1/),gr_O_diff_hollow_bridge_r(cell + (/ 1, 0, 0, 0/)))
    end if
    if(can_do(O_diff_hollow_bridge_r,cell + (/ -1, 0, 0, 1/))) then
        call update_rates_matrix(O_diff_hollow_bridge_r,cell + (/ -1, 0, 0, 1/),gr_O_diff_hollow_bridge_r(cell + (/ -1, 0, 0, 0/)))
    end if
    if(can_do(O_diff_hollow_hollow_l,cell + (/ -1, 0, 0, 1/))) then
        call update_rates_matrix(O_diff_hollow_hollow_l,cell + (/ -1, 0, 0, 1/),gr_O_diff_hollow_hollow_l(cell + (/ -1, 0, 0, 0/)))
    end if
    if(can_do(O_diff_hollow_hollow_l,cell + (/ 2, 0, 0, 1/))) then
        call update_rates_matrix(O_diff_hollow_hollow_l,cell + (/ 2, 0, 0, 1/),gr_O_diff_hollow_hollow_l(cell + (/ 2, 0, 0, 0/)))
    end if
    if(can_do(O_diff_hollow_hollow_r,cell + (/ 1, 0, 0, 1/))) then
        call update_rates_matrix(O_diff_hollow_hollow_r,cell + (/ 1, 0, 0, 1/),gr_O_diff_hollow_hollow_r(cell + (/ 1, 0, 0, 0/)))
    end if
    if(can_do(O_diff_hollow_hollow_r,cell + (/ -2, 0, 0, 1/))) then
        call update_rates_matrix(O_diff_hollow_hollow_r,cell + (/ -2, 0, 0, 1/),gr_O_diff_hollow_hollow_r(cell + (/ -2, 0, 0, 0/)))
    end if
    if(can_do(O_diff_hollow_hollow_r,cell + (/ -1, 0, 0, 1/))) then
        call update_rates_matrix(O_diff_hollow_hollow_r,cell + (/ -1, 0, 0, 1/),gr_O_diff_hollow_hollow_r(cell + (/ -1, 0, 0, 0/)))
    end if

! Enable processes

    call add_proc(CO_ads_hollow, cell + (/ 0, 0, 0, 1/), gr_CO_ads_hollow(cell + (/ 0, 0, 0, 0/)))
    call add_proc(CO_des_bridge, cell + (/ 1, 0, 0, 1/), gr_CO_des_bridge(cell + (/ 1, 0, 0, 0/)))
    call add_proc(CO_diff_bridge_hollow_l, cell + (/ 1, 0, 0, 1/), gr_CO_diff_bridge_hollow_l(cell + (/ 1, 0, 0, 0/)))
    select case(get_species(cell + (/0, 0, 0, pdo_bridge/)))
    case(CO)
        call add_proc(CO_diff_bridge_hollow, cell + (/ 0, 0, 0, 1/), gr_CO_diff_bridge_hollow(cell + (/ 0, 0, 0, 0/)))
    case(O)
        call add_proc(CO_oxi_bridge_bridge_r, cell + (/ 0, 0, 0, 1/), gr_CO_oxi_bridge_bridge_r(cell + (/ 0, 0, 0, 0/)))
        call add_proc(O_diff_bridge_hollow, cell + (/ 0, 0, 0, 1/), gr_O_diff_bridge_hollow(cell + (/ 0, 0, 0, 0/)))
    case(empty)
        call add_proc(CO_diff_bridge_bridge_l, cell + (/ 1, 0, 0, 1/), gr_CO_diff_bridge_bridge_l(cell + (/ 1, 0, 0, 0/)))
        call add_proc(O2_ads_bridge_hollow, cell + (/ 0, 0, 0, 1/), gr_O2_ads_bridge_hollow(cell + (/ 0, 0, 0, 0/)))
    end select

    select case(get_species(cell + (/1, 0, 0, pdo_hollow/)))
    case(CO)
        call add_proc(CO_diff_hollow_hollow_l, cell + (/ 1, 0, 0, 1/), gr_CO_diff_hollow_hollow_l(cell + (/ 1, 0, 0, 0/)))
    case(O)
        call add_proc(CO_oxi_hollow_bridge, cell + (/ 1, 0, 0, 1/), gr_CO_oxi_hollow_bridge(cell + (/ 1, 0, 0, 0/)))
        call add_proc(O_diff_hollow_hollow_l, cell + (/ 1, 0, 0, 1/), gr_O_diff_hollow_hollow_l(cell + (/ 1, 0, 0, 0/)))
    case(empty)
        call add_proc(CO_diff_bridge_hollow, cell + (/ 1, 0, 0, 1/), gr_CO_diff_bridge_hollow(cell + (/ 1, 0, 0, 0/)))
        call add_proc(O2_ads_hollow_hollow, cell + (/ 0, 0, 0, 1/), gr_O2_ads_hollow_hollow(cell + (/ 0, 0, 0, 0/)))
    end select

    select case(get_species(cell + (/-1, 0, 0, pdo_hollow/)))
    case(CO)
        call add_proc(CO_diff_hollow_hollow_r, cell + (/ -1, 0, 0, 1/), gr_CO_diff_hollow_hollow_r(cell + (/ -1, 0, 0, 0/)))
    case(O)
        call add_proc(O_diff_hollow_hollow_r, cell + (/ -1, 0, 0, 1/), gr_O_diff_hollow_hollow_r(cell + (/ -1, 0, 0, 0/)))
    case(empty)
        call add_proc(O2_ads_hollow_hollow, cell + (/ -1, 0, 0, 1/), gr_O2_ads_hollow_hollow(cell + (/ -1, 0, 0, 0/)))
    end select

    select case(get_species(cell + (/2, 0, 0, pdo_bridge/)))
    case(O)
        call add_proc(CO_oxi_bridge_bridge_l, cell + (/ 2, 0, 0, 1/), gr_CO_oxi_bridge_bridge_l(cell + (/ 2, 0, 0, 0/)))
    case(empty)
        call add_proc(CO_diff_bridge_bridge_r, cell + (/ 1, 0, 0, 1/), gr_CO_diff_bridge_bridge_r(cell + (/ 1, 0, 0, 0/)))
    end select


end subroutine run_proc_CO_diff_hollow_bridge_r

end module run_proc_0010
