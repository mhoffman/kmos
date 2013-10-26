module nli_0018
use kind_values
use lattice
use proclist_constants
implicit none
contains
pure function nli_reaction_oxygen_cus_co_cus_down(cell)
    integer(kind=iint), dimension(4), intent(in) :: cell
    integer(kind=iint) :: nli_reaction_oxygen_cus_co_cus_down

    select case(get_species(cell + (/0, -1, 0, ruo2_cus/)))
      case(co)
        select case(get_species(cell + (/0, 0, 0, ruo2_cus/)))
          case(oxygen)
            nli_reaction_oxygen_cus_co_cus_down = reaction_oxygen_cus_co_cus_down; return
          case default
            nli_reaction_oxygen_cus_co_cus_down = 0; return
        end select
      case default
        nli_reaction_oxygen_cus_co_cus_down = 0; return
    end select

end function nli_reaction_oxygen_cus_co_cus_down

end module
