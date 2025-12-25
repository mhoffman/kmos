module nli_0039
use kind_values
use lattice
use proclist_constants
implicit none
contains
pure function nli_o_COdif_h1h2down(cell)
    integer(kind=iint), dimension(4), intent(in) :: cell
    integer(kind=iint) :: nli_o_COdif_h1h2down

    select case(get_species(cell + (/0, -1, 0, PdO_hollow2/)))
      case(empty)
        select case(get_species(cell + (/0, 0, 0, PdO_hollow1/)))
          case(CO)
            nli_o_COdif_h1h2down = o_COdif_h1h2down; return
          case default
            nli_o_COdif_h1h2down = 0; return
        end select
      case default
        nli_o_COdif_h1h2down = 0; return
    end select

end function nli_o_COdif_h1h2down

end module
