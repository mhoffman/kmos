module run_proc_0029
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
subroutine run_proc_m_COads_b9(cell)

    integer(kind=iint), dimension(4), intent(in) :: cell

    ! disable processes that have to be disabled
    call del_proc(nli_m_COads_b9(cell + (/+0, +0, +0, 0/)), cell + (/+0, +0, +0, 1/))
    call del_proc(nli_m_COdes_b9(cell + (/+0, +0, +0, 0/)), cell + (/+0, +0, +0, 1/))
    call del_proc(nli_oxidize1(cell + (/+0, +0, +0, 0/)), cell + (/+0, +0, +0, 1/))

    ! update lattice
    call replace_species(cell + (/0, 0, 0, Pd100_b9/), empty, CO)

    ! enable processes that have to be enabled
    call add_proc(nli_m_COads_b9(cell + (/+0, +0, +0, 0/)), cell + (/+0, +0, +0, 1/))
    call add_proc(nli_m_COdes_b9(cell + (/+0, +0, +0, 0/)), cell + (/+0, +0, +0, 1/))
    call add_proc(nli_oxidize1(cell + (/+0, +0, +0, 0/)), cell + (/+0, +0, +0, 1/))

end subroutine run_proc_m_COads_b9

end module
