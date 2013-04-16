module nli_0013
use kind_values
use lattice
use proclist_constants
implicit none
contains
pure function nli_oxygen_desorption_bridge_cus_left(cell)
    integer(kind=iint), dimension(4), intent(in) :: cell
    integer(kind=iint) :: nli_oxygen_desorption_bridge_cus_left

    select case(get_species(cell + (/-1, 0, 0, ruo2_cus/)))
      case(oxygen)
        select case(get_species(cell + (/0, 0, 0, ruo2_bridge/)))
          case(oxygen)
            nli_oxygen_desorption_bridge_cus_left = oxygen_desorption_bridge_cus_left; return
          case default
            nli_oxygen_desorption_bridge_cus_left = 0; return
        end select
      case default
        nli_oxygen_desorption_bridge_cus_left = 0; return
    end select

end function nli_oxygen_desorption_bridge_cus_left

end module
