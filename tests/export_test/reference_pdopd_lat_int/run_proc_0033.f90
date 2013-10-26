module run_proc_0033
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
use nli_0036
use nli_0037
use nli_0038
use nli_0039
use nli_0040
use nli_0041
use nli_0042
use nli_0043
use nli_0044
use nli_0045
use proclist_constants
implicit none
contains
subroutine run_proc_o_COdif_h1h2down(cell)

    integer(kind=iint), dimension(4), intent(in) :: cell

    ! disable processes that have to be disabled
    call del_proc(nli_destruct1(cell + (/+0, +0, +0, 0/)), cell + (/+0, +0, +0, 1/))
    call del_proc(nli_destruct10(cell + (/+0, +0, +0, 0/)), cell + (/+0, +0, +0, 1/))
    call del_proc(nli_destruct11(cell + (/+0, +0, +0, 0/)), cell + (/+0, +0, +0, 1/))
    call del_proc(nli_destruct2(cell + (/+0, +0, +0, 0/)), cell + (/+0, +0, +0, 1/))
    call del_proc(nli_destruct3(cell + (/+0, +0, +0, 0/)), cell + (/+0, +0, +0, 1/))
    call del_proc(nli_destruct4(cell + (/+0, +0, +0, 0/)), cell + (/+0, +0, +0, 1/))
    call del_proc(nli_destruct5(cell + (/+0, +0, +0, 0/)), cell + (/+0, +0, +0, 1/))
    call del_proc(nli_destruct6(cell + (/+0, +0, +0, 0/)), cell + (/+0, +0, +0, 1/))
    call del_proc(nli_destruct7(cell + (/+0, +0, +0, 0/)), cell + (/+0, +0, +0, 1/))
    call del_proc(nli_destruct8(cell + (/+0, +0, +0, 0/)), cell + (/+0, +0, +0, 1/))
    call del_proc(nli_destruct9(cell + (/+0, +0, +0, 0/)), cell + (/+0, +0, +0, 1/))
    call del_proc(nli_o_COads_hollow1(cell + (/+0, +0, +0, 0/)), cell + (/+0, +0, +0, 1/))
    call del_proc(nli_o_COads_hollow2(cell + (/+0, -1, +0, 0/)), cell + (/+0, -1, +0, 1/))
    call del_proc(nli_o_COdes_hollow1(cell + (/+0, +0, +0, 0/)), cell + (/+0, +0, +0, 1/))
    call del_proc(nli_o_COdes_hollow2(cell + (/+0, -1, +0, 0/)), cell + (/+0, -1, +0, 1/))
    call del_proc(nli_o_COdif_h1h2down(cell + (/+0, +0, +0, 0/)), cell + (/+0, +0, +0, 1/))
    call del_proc(nli_o_COdif_h1h2up(cell + (/+0, -1, +0, 0/)), cell + (/+0, -1, +0, 1/))
    call del_proc(nli_o_COdif_h1h2up(cell + (/+0, +0, +0, 0/)), cell + (/+0, +0, +0, 1/))
    call del_proc(nli_o_O2ads_h1h2(cell + (/+0, -1, +0, 0/)), cell + (/+0, -1, +0, 1/))
    call del_proc(nli_o_O2ads_h1h2(cell + (/+0, +0, +0, 0/)), cell + (/+0, +0, +0, 1/))
    call del_proc(nli_o_O2ads_h2h1(cell + (/+0, -1, +0, 0/)), cell + (/+0, -1, +0, 1/))
    call del_proc(nli_o_O2des_h1h2(cell + (/+0, -1, +0, 0/)), cell + (/+0, -1, +0, 1/))
    call del_proc(nli_o_O2des_h1h2(cell + (/+0, +0, +0, 0/)), cell + (/+0, +0, +0, 1/))
    call del_proc(nli_o_O2des_h2h1(cell + (/+0, -1, +0, 0/)), cell + (/+0, -1, +0, 1/))

    ! update lattice
    call replace_species(cell + (/0, 0, 0, PdO_hollow1/), CO, empty)
    call replace_species(cell + (/0, -1, 0, PdO_hollow2/), empty, CO)

    ! enable processes that have to be enabled
    call add_proc(nli_destruct1(cell + (/+0, +0, +0, 0/)), cell + (/+0, +0, +0, 1/))
    call add_proc(nli_destruct10(cell + (/+0, +0, +0, 0/)), cell + (/+0, +0, +0, 1/))
    call add_proc(nli_destruct11(cell + (/+0, +0, +0, 0/)), cell + (/+0, +0, +0, 1/))
    call add_proc(nli_destruct2(cell + (/+0, +0, +0, 0/)), cell + (/+0, +0, +0, 1/))
    call add_proc(nli_destruct3(cell + (/+0, +0, +0, 0/)), cell + (/+0, +0, +0, 1/))
    call add_proc(nli_destruct4(cell + (/+0, +0, +0, 0/)), cell + (/+0, +0, +0, 1/))
    call add_proc(nli_destruct5(cell + (/+0, +0, +0, 0/)), cell + (/+0, +0, +0, 1/))
    call add_proc(nli_destruct6(cell + (/+0, +0, +0, 0/)), cell + (/+0, +0, +0, 1/))
    call add_proc(nli_destruct7(cell + (/+0, +0, +0, 0/)), cell + (/+0, +0, +0, 1/))
    call add_proc(nli_destruct8(cell + (/+0, +0, +0, 0/)), cell + (/+0, +0, +0, 1/))
    call add_proc(nli_destruct9(cell + (/+0, +0, +0, 0/)), cell + (/+0, +0, +0, 1/))
    call add_proc(nli_o_COads_hollow1(cell + (/+0, +0, +0, 0/)), cell + (/+0, +0, +0, 1/))
    call add_proc(nli_o_COads_hollow2(cell + (/+0, -1, +0, 0/)), cell + (/+0, -1, +0, 1/))
    call add_proc(nli_o_COdes_hollow1(cell + (/+0, +0, +0, 0/)), cell + (/+0, +0, +0, 1/))
    call add_proc(nli_o_COdes_hollow2(cell + (/+0, -1, +0, 0/)), cell + (/+0, -1, +0, 1/))
    call add_proc(nli_o_COdif_h1h2down(cell + (/+0, +0, +0, 0/)), cell + (/+0, +0, +0, 1/))
    call add_proc(nli_o_COdif_h1h2up(cell + (/+0, -1, +0, 0/)), cell + (/+0, -1, +0, 1/))
    call add_proc(nli_o_COdif_h1h2up(cell + (/+0, +0, +0, 0/)), cell + (/+0, +0, +0, 1/))
    call add_proc(nli_o_O2ads_h1h2(cell + (/+0, -1, +0, 0/)), cell + (/+0, -1, +0, 1/))
    call add_proc(nli_o_O2ads_h1h2(cell + (/+0, +0, +0, 0/)), cell + (/+0, +0, +0, 1/))
    call add_proc(nli_o_O2ads_h2h1(cell + (/+0, -1, +0, 0/)), cell + (/+0, -1, +0, 1/))
    call add_proc(nli_o_O2des_h1h2(cell + (/+0, -1, +0, 0/)), cell + (/+0, -1, +0, 1/))
    call add_proc(nli_o_O2des_h1h2(cell + (/+0, +0, +0, 0/)), cell + (/+0, +0, +0, 1/))
    call add_proc(nli_o_O2des_h2h1(cell + (/+0, -1, +0, 0/)), cell + (/+0, -1, +0, 1/))

end subroutine run_proc_o_COdif_h1h2down

end module
