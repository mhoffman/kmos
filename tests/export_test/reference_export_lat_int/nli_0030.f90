module nli_0030
use kind_values
use lattice
use proclist_constants
implicit none
contains
pure function nli_reaction_oxygen_bridge_co_cus_left(cell)
    integer(kind=iint), dimension(4), intent(in) :: cell
    integer(kind=iint) :: nli_reaction_oxygen_bridge_co_cus_left

    select case(get_species(cell + (/-1, 0, 0, ruo2_cus/)))
      case(co)
        select case(get_species(cell + (/0, 0, 0, ruo2_bridge/)))
          case(oxygen)
            nli_reaction_oxygen_bridge_co_cus_left = reaction_oxygen_bridge_co_cus_left; return
          case default
            nli_reaction_oxygen_bridge_co_cus_left = 0; return
        end select
      case default
        nli_reaction_oxygen_bridge_co_cus_left = 0; return
    end select

end function nli_reaction_oxygen_bridge_co_cus_left

end module
