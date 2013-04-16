module nli_0028
use kind_values
use lattice
use proclist_constants
implicit none
contains
pure function nli_reaction_oxygen_cus_co_bridge_left(cell)
    integer(kind=iint), dimension(4), intent(in) :: cell
    integer(kind=iint) :: nli_reaction_oxygen_cus_co_bridge_left

    select case(get_species(cell + (/0, 0, 0, ruo2_cus/)))
      case(oxygen)
        select case(get_species(cell + (/0, 0, 0, ruo2_bridge/)))
          case(co)
            nli_reaction_oxygen_cus_co_bridge_left = reaction_oxygen_cus_co_bridge_left; return
          case default
            nli_reaction_oxygen_cus_co_bridge_left = 0; return
        end select
      case default
        nli_reaction_oxygen_cus_co_bridge_left = 0; return
    end select

end function nli_reaction_oxygen_cus_co_bridge_left

end module
