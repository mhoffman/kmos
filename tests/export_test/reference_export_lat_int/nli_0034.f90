module nli_0034
use kind_values
use lattice
use proclist_constants
implicit none
contains
pure function nli_co_adsorption_bridge(cell)
    integer(kind=iint), dimension(4), intent(in) :: cell
    integer(kind=iint) :: nli_co_adsorption_bridge

    select case(get_species(cell + (/0, 0, 0, ruo2_bridge/)))
      case(empty)
        nli_co_adsorption_bridge = co_adsorption_bridge; return
      case default
        nli_co_adsorption_bridge = 0; return
    end select

end function nli_co_adsorption_bridge

end module
