module nli_0019
use kind_values
use lattice
use proclist_constants
implicit none
contains
pure function nli_o_COads_hollow1(cell)
    integer(kind=iint), dimension(4), intent(in) :: cell
    integer(kind=iint) :: nli_o_COads_hollow1

    select case(get_species(cell + (/0, 0, 0, PdO_hollow1/)))
      case(empty)
        nli_o_COads_hollow1 = o_COads_hollow1; return
      case default
        nli_o_COads_hollow1 = 0; return
    end select

end function nli_o_COads_hollow1

end module
