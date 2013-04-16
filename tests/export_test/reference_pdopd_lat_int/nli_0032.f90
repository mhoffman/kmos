module nli_0032
use kind_values
use lattice
use proclist_constants
implicit none
contains
pure function nli_o_COdes_bridge1(cell)
    integer(kind=iint), dimension(4), intent(in) :: cell
    integer(kind=iint) :: nli_o_COdes_bridge1

    select case(get_species(cell + (/0, 0, 0, PdO_bridge1/)))
      case(CO)
        nli_o_COdes_bridge1 = o_COdes_bridge1; return
      case default
        nli_o_COdes_bridge1 = 0; return
    end select

end function nli_o_COdes_bridge1

end module
