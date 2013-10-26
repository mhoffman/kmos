module nli_0034
use kind_values
use lattice
use proclist_constants
implicit none
contains
pure function nli_o_O2des_h2h1(cell)
    integer(kind=iint), dimension(4), intent(in) :: cell
    integer(kind=iint) :: nli_o_O2des_h2h1

    select case(get_species(cell + (/0, 0, 0, PdO_hollow2/)))
      case(oxygen)
        select case(get_species(cell + (/0, 1, 0, PdO_hollow1/)))
          case(oxygen)
            nli_o_O2des_h2h1 = o_O2des_h2h1; return
          case default
            nli_o_O2des_h2h1 = 0; return
        end select
      case default
        nli_o_O2des_h2h1 = 0; return
    end select

end function nli_o_O2des_h2h1

end module
