module nli_0032
use kind_values
use lattice
use proclist_constants
implicit none
contains
pure function nli_co_desorption_bridge(cell)
    integer(kind=iint), dimension(4), intent(in) :: cell
    integer(kind=iint) :: nli_co_desorption_bridge

    select case(get_species(cell + (/0, 0, 0, ruo2_bridge/)))
      case(co)
        nli_co_desorption_bridge = co_desorption_bridge; return
      case default
        nli_co_desorption_bridge = 0; return
    end select

end function nli_co_desorption_bridge

end module
