module run_proc_0002

use kind_values
use lattice
use proclist_pars

implicit none
contains

subroutine run_proc_CO_des(cell)

    integer(kind=iint), dimension(4), intent(in) :: cell


! Disable processes

    if(can_do(CO_des,cell + (/ 0, 0, 0, 1/))) then
        call del_proc(CO_des,cell + (/ 0, 0, 0, 1/))
    end if
    if(can_do(CO_oxidation_00,cell + (/ -1, 0, 0, 1/))) then
        call del_proc(CO_oxidation_00,cell + (/ -1, 0, 0, 1/))
    end if
    if(can_do(CO_oxidation_00,cell + (/ 0, 0, 0, 1/))) then
        call del_proc(CO_oxidation_00,cell + (/ 0, 0, 0, 1/))
    end if
    if(can_do(CO_oxidation_01,cell + (/ 0, 0, 0, 1/))) then
        call del_proc(CO_oxidation_01,cell + (/ 0, 0, 0, 1/))
    end if
    if(can_do(CO_oxidation_01,cell + (/ 0, -1, 0, 1/))) then
        call del_proc(CO_oxidation_01,cell + (/ 0, -1, 0, 1/))
    end if
    if(can_do(CO_oxidation_02,cell + (/ 1, 0, 0, 1/))) then
        call del_proc(CO_oxidation_02,cell + (/ 1, 0, 0, 1/))
    end if
    if(can_do(CO_oxidation_02,cell + (/ 0, 0, 0, 1/))) then
        call del_proc(CO_oxidation_02,cell + (/ 0, 0, 0, 1/))
    end if
    if(can_do(CO_oxidation_03,cell + (/ 0, 1, 0, 1/))) then
        call del_proc(CO_oxidation_03,cell + (/ 0, 1, 0, 1/))
    end if
    if(can_do(CO_oxidation_03,cell + (/ 0, 0, 0, 1/))) then
        call del_proc(CO_oxidation_03,cell + (/ 0, 0, 0, 1/))
    end if
    if(can_do(O2_des_right,cell + (/ -1, 0, 0, 1/))) then
        call del_proc(O2_des_right,cell + (/ -1, 0, 0, 1/))
    end if
    if(can_do(O2_des_right,cell + (/ 0, 0, 0, 1/))) then
        call del_proc(O2_des_right,cell + (/ 0, 0, 0, 1/))
    end if
    if(can_do(O2_des_up,cell + (/ 0, 0, 0, 1/))) then
        call del_proc(O2_des_up,cell + (/ 0, 0, 0, 1/))
    end if
    if(can_do(O2_des_up,cell + (/ 0, -1, 0, 1/))) then
        call del_proc(O2_des_up,cell + (/ 0, -1, 0, 1/))
    end if

! Update the lattice
    call replace_species(cell + (/0, 0, 0, square_default/),CO,empty)

! Update rate constants

    if(can_do(CO_ads,cell + (/ 1, 0, 0, 1/))) then
        call update_rates_matrix(CO_ads,cell + (/ 1, 0, 0, 1/),gr_CO_ads(cell + (/ 1, 0, 0, 0/)))
    end if
    if(can_do(CO_ads,cell + (/ -1, 0, 0, 1/))) then
        call update_rates_matrix(CO_ads,cell + (/ -1, 0, 0, 1/),gr_CO_ads(cell + (/ -1, 0, 0, 0/)))
    end if
    if(can_do(CO_ads,cell + (/ 0, 1, 0, 1/))) then
        call update_rates_matrix(CO_ads,cell + (/ 0, 1, 0, 1/),gr_CO_ads(cell + (/ 0, 1, 0, 0/)))
    end if
    if(can_do(CO_ads,cell + (/ 0, -1, 0, 1/))) then
        call update_rates_matrix(CO_ads,cell + (/ 0, -1, 0, 1/),gr_CO_ads(cell + (/ 0, -1, 0, 0/)))
    end if
    if(can_do(CO_oxidation_00,cell + (/ -1, 1, 0, 1/))) then
        call update_rates_matrix(CO_oxidation_00,cell + (/ -1, 1, 0, 1/),gr_CO_oxidation_00(cell + (/ -1, 1, 0, 0/)))
    end if
    if(can_do(CO_oxidation_00,cell + (/ 1, 0, 0, 1/))) then
        call update_rates_matrix(CO_oxidation_00,cell + (/ 1, 0, 0, 1/),gr_CO_oxidation_00(cell + (/ 1, 0, 0, 0/)))
    end if
    if(can_do(CO_oxidation_00,cell + (/ -1, -1, 0, 1/))) then
        call update_rates_matrix(CO_oxidation_00,cell + (/ -1, -1, 0, 1/),gr_CO_oxidation_00(cell + (/ -1, -1, 0, 0/)))
    end if
    if(can_do(CO_oxidation_00,cell + (/ 0, -1, 0, 1/))) then
        call update_rates_matrix(CO_oxidation_00,cell + (/ 0, -1, 0, 1/),gr_CO_oxidation_00(cell + (/ 0, -1, 0, 0/)))
    end if
    if(can_do(CO_oxidation_00,cell + (/ -2, 0, 0, 1/))) then
        call update_rates_matrix(CO_oxidation_00,cell + (/ -2, 0, 0, 1/),gr_CO_oxidation_00(cell + (/ -2, 0, 0, 0/)))
    end if
    if(can_do(CO_oxidation_00,cell + (/ 0, 1, 0, 1/))) then
        call update_rates_matrix(CO_oxidation_00,cell + (/ 0, 1, 0, 1/),gr_CO_oxidation_00(cell + (/ 0, 1, 0, 0/)))
    end if
    if(can_do(CO_oxidation_01,cell + (/ 1, 0, 0, 1/))) then
        call update_rates_matrix(CO_oxidation_01,cell + (/ 1, 0, 0, 1/),gr_CO_oxidation_01(cell + (/ 1, 0, 0, 0/)))
    end if
    if(can_do(CO_oxidation_01,cell + (/ 1, -1, 0, 1/))) then
        call update_rates_matrix(CO_oxidation_01,cell + (/ 1, -1, 0, 1/),gr_CO_oxidation_01(cell + (/ 1, -1, 0, 0/)))
    end if
    if(can_do(CO_oxidation_01,cell + (/ -1, -1, 0, 1/))) then
        call update_rates_matrix(CO_oxidation_01,cell + (/ -1, -1, 0, 1/),gr_CO_oxidation_01(cell + (/ -1, -1, 0, 0/)))
    end if
    if(can_do(CO_oxidation_01,cell + (/ 0, -2, 0, 1/))) then
        call update_rates_matrix(CO_oxidation_01,cell + (/ 0, -2, 0, 1/),gr_CO_oxidation_01(cell + (/ 0, -2, 0, 0/)))
    end if
    if(can_do(CO_oxidation_01,cell + (/ -1, 0, 0, 1/))) then
        call update_rates_matrix(CO_oxidation_01,cell + (/ -1, 0, 0, 1/),gr_CO_oxidation_01(cell + (/ -1, 0, 0, 0/)))
    end if
    if(can_do(CO_oxidation_01,cell + (/ 0, 1, 0, 1/))) then
        call update_rates_matrix(CO_oxidation_01,cell + (/ 0, 1, 0, 1/),gr_CO_oxidation_01(cell + (/ 0, 1, 0, 0/)))
    end if
    if(can_do(CO_oxidation_02,cell + (/ 1, 1, 0, 1/))) then
        call update_rates_matrix(CO_oxidation_02,cell + (/ 1, 1, 0, 1/),gr_CO_oxidation_02(cell + (/ 1, 1, 0, 0/)))
    end if
    if(can_do(CO_oxidation_02,cell + (/ 1, -1, 0, 1/))) then
        call update_rates_matrix(CO_oxidation_02,cell + (/ 1, -1, 0, 1/),gr_CO_oxidation_02(cell + (/ 1, -1, 0, 0/)))
    end if
    if(can_do(CO_oxidation_02,cell + (/ 0, -1, 0, 1/))) then
        call update_rates_matrix(CO_oxidation_02,cell + (/ 0, -1, 0, 1/),gr_CO_oxidation_02(cell + (/ 0, -1, 0, 0/)))
    end if
    if(can_do(CO_oxidation_02,cell + (/ -1, 0, 0, 1/))) then
        call update_rates_matrix(CO_oxidation_02,cell + (/ -1, 0, 0, 1/),gr_CO_oxidation_02(cell + (/ -1, 0, 0, 0/)))
    end if
    if(can_do(CO_oxidation_02,cell + (/ 0, 1, 0, 1/))) then
        call update_rates_matrix(CO_oxidation_02,cell + (/ 0, 1, 0, 1/),gr_CO_oxidation_02(cell + (/ 0, 1, 0, 0/)))
    end if
    if(can_do(CO_oxidation_02,cell + (/ 2, 0, 0, 1/))) then
        call update_rates_matrix(CO_oxidation_02,cell + (/ 2, 0, 0, 1/),gr_CO_oxidation_02(cell + (/ 2, 0, 0, 0/)))
    end if
    if(can_do(CO_oxidation_03,cell + (/ -1, 1, 0, 1/))) then
        call update_rates_matrix(CO_oxidation_03,cell + (/ -1, 1, 0, 1/),gr_CO_oxidation_03(cell + (/ -1, 1, 0, 0/)))
    end if
    if(can_do(CO_oxidation_03,cell + (/ 0, 2, 0, 1/))) then
        call update_rates_matrix(CO_oxidation_03,cell + (/ 0, 2, 0, 1/),gr_CO_oxidation_03(cell + (/ 0, 2, 0, 0/)))
    end if
    if(can_do(CO_oxidation_03,cell + (/ 1, 1, 0, 1/))) then
        call update_rates_matrix(CO_oxidation_03,cell + (/ 1, 1, 0, 1/),gr_CO_oxidation_03(cell + (/ 1, 1, 0, 0/)))
    end if
    if(can_do(CO_oxidation_03,cell + (/ 1, 0, 0, 1/))) then
        call update_rates_matrix(CO_oxidation_03,cell + (/ 1, 0, 0, 1/),gr_CO_oxidation_03(cell + (/ 1, 0, 0, 0/)))
    end if
    if(can_do(CO_oxidation_03,cell + (/ 0, -1, 0, 1/))) then
        call update_rates_matrix(CO_oxidation_03,cell + (/ 0, -1, 0, 1/),gr_CO_oxidation_03(cell + (/ 0, -1, 0, 0/)))
    end if
    if(can_do(CO_oxidation_03,cell + (/ -1, 0, 0, 1/))) then
        call update_rates_matrix(CO_oxidation_03,cell + (/ -1, 0, 0, 1/),gr_CO_oxidation_03(cell + (/ -1, 0, 0, 0/)))
    end if
    if(can_do(O_ads_00,cell + (/ -1, 1, 0, 1/))) then
        call update_rates_matrix(O_ads_00,cell + (/ -1, 1, 0, 1/),gr_O_ads_00(cell + (/ -1, 1, 0, 0/)))
    end if
    if(can_do(O_ads_00,cell + (/ 1, 0, 0, 1/))) then
        call update_rates_matrix(O_ads_00,cell + (/ 1, 0, 0, 1/),gr_O_ads_00(cell + (/ 1, 0, 0, 0/)))
    end if
    if(can_do(O_ads_00,cell + (/ -1, -1, 0, 1/))) then
        call update_rates_matrix(O_ads_00,cell + (/ -1, -1, 0, 1/),gr_O_ads_00(cell + (/ -1, -1, 0, 0/)))
    end if
    if(can_do(O_ads_00,cell + (/ 0, -1, 0, 1/))) then
        call update_rates_matrix(O_ads_00,cell + (/ 0, -1, 0, 1/),gr_O_ads_00(cell + (/ 0, -1, 0, 0/)))
    end if
    if(can_do(O_ads_00,cell + (/ -2, 0, 0, 1/))) then
        call update_rates_matrix(O_ads_00,cell + (/ -2, 0, 0, 1/),gr_O_ads_00(cell + (/ -2, 0, 0, 0/)))
    end if
    if(can_do(O_ads_00,cell + (/ 0, 1, 0, 1/))) then
        call update_rates_matrix(O_ads_00,cell + (/ 0, 1, 0, 1/),gr_O_ads_00(cell + (/ 0, 1, 0, 0/)))
    end if
    if(can_do(O_ads_01,cell + (/ 1, 0, 0, 1/))) then
        call update_rates_matrix(O_ads_01,cell + (/ 1, 0, 0, 1/),gr_O_ads_01(cell + (/ 1, 0, 0, 0/)))
    end if
    if(can_do(O_ads_01,cell + (/ 1, -1, 0, 1/))) then
        call update_rates_matrix(O_ads_01,cell + (/ 1, -1, 0, 1/),gr_O_ads_01(cell + (/ 1, -1, 0, 0/)))
    end if
    if(can_do(O_ads_01,cell + (/ -1, -1, 0, 1/))) then
        call update_rates_matrix(O_ads_01,cell + (/ -1, -1, 0, 1/),gr_O_ads_01(cell + (/ -1, -1, 0, 0/)))
    end if
    if(can_do(O_ads_01,cell + (/ 0, -2, 0, 1/))) then
        call update_rates_matrix(O_ads_01,cell + (/ 0, -2, 0, 1/),gr_O_ads_01(cell + (/ 0, -2, 0, 0/)))
    end if
    if(can_do(O_ads_01,cell + (/ -1, 0, 0, 1/))) then
        call update_rates_matrix(O_ads_01,cell + (/ -1, 0, 0, 1/),gr_O_ads_01(cell + (/ -1, 0, 0, 0/)))
    end if
    if(can_do(O_ads_01,cell + (/ 0, 1, 0, 1/))) then
        call update_rates_matrix(O_ads_01,cell + (/ 0, 1, 0, 1/),gr_O_ads_01(cell + (/ 0, 1, 0, 0/)))
    end if

! Enable processes

    call add_proc(CO_ads, cell + (/ 0, 0, 0, 1/), gr_CO_ads(cell + (/ 0, 0, 0, 0/)))
    select case(get_species(cell + (/-1, 0, 0, square_default/)))
    case(empty)
        call add_proc(O_ads_00, cell + (/ -1, 0, 0, 1/), gr_O_ads_00(cell + (/ -1, 0, 0, 0/)))
    end select

    select case(get_species(cell + (/1, 0, 0, square_default/)))
    case(empty)
        call add_proc(O_ads_00, cell + (/ 0, 0, 0, 1/), gr_O_ads_00(cell + (/ 0, 0, 0, 0/)))
    end select

    select case(get_species(cell + (/0, 1, 0, square_default/)))
    case(empty)
        call add_proc(O_ads_01, cell + (/ 0, 0, 0, 1/), gr_O_ads_01(cell + (/ 0, 0, 0, 0/)))
    end select

    select case(get_species(cell + (/0, -1, 0, square_default/)))
    case(empty)
        call add_proc(O_ads_01, cell + (/ 0, -1, 0, 1/), gr_O_ads_01(cell + (/ 0, -1, 0, 0/)))
    end select


end subroutine run_proc_CO_des

end module run_proc_0002
