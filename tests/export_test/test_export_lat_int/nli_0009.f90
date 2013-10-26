module nli_0009
use kind_values
use lattice
use proclist_constants
implicit none
contains
pure function nli_oxygen_adsorption_bridge_bridge(cell)
    integer(kind=iint), dimension(4), intent(in) :: cell
    integer(kind=iint) :: nli_oxygen_adsorption_bridge_bridge

    select case(get_species(cell + (/0, 0, 0, ruo2_bridge/)))
      case(empty)
        select case(get_species(cell + (/0, 1, 0, ruo2_bridge/)))
          case(empty)
            nli_oxygen_adsorption_bridge_bridge = oxygen_adsorption_bridge_bridge; return
          case default
            nli_oxygen_adsorption_bridge_bridge = 0; return
        end select
      case default
        nli_oxygen_adsorption_bridge_bridge = 0; return
    end select

end function nli_oxygen_adsorption_bridge_bridge

end module
