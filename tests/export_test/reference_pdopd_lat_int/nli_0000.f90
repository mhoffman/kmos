module nli_0000
use kind_values
use lattice
use proclist_constants
implicit none
contains
pure function nli_destruct9(cell)
    integer(kind=iint), dimension(4), intent(in) :: cell
    integer(kind=iint) :: nli_destruct9

    select case(get_species(cell + (/0, -1, 0, PdO_hollow2/)))
      case(empty)
        select case(get_species(cell + (/0, -1, 0, PdO_bridge2/)))
          case(CO)
            select case(get_species(cell + (/0, 0, 0, PdO_hollow1/)))
              case(CO)
                select case(get_species(cell + (/0, 0, 0, PdO_bridge1/)))
                  case(empty)
                    nli_destruct9 = destruct9; return
                  case default
                    nli_destruct9 = 0; return
                end select
              case default
                nli_destruct9 = 0; return
            end select
          case default
            nli_destruct9 = 0; return
        end select
      case default
        nli_destruct9 = 0; return
    end select

end function nli_destruct9

end module
