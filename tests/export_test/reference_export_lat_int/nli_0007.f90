module nli_0007
use kind_values
use lattice
use proclist_constants
implicit none
contains
pure function nli_reaction_oxygen_bridge_co_bridge_up(cell)
    integer(kind=iint), dimension(4), intent(in) :: cell
    integer(kind=iint) :: nli_reaction_oxygen_bridge_co_bridge_up

    select case(get_species(cell + (/0, 0, 0, ruo2_bridge/)))
      case(oxygen)
        select case(get_species(cell + (/0, 1, 0, ruo2_bridge/)))
          case(co)
            nli_reaction_oxygen_bridge_co_bridge_up = reaction_oxygen_bridge_co_bridge_up; return
          case default
            nli_reaction_oxygen_bridge_co_bridge_up = 0; return
        end select
      case default
        nli_reaction_oxygen_bridge_co_bridge_up = 0; return
    end select

end function nli_reaction_oxygen_bridge_co_bridge_up

end module
