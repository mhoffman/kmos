module nli_0038
use kind_values
use lattice
use proclist_constants
implicit none
contains
pure function nli_destruct11(cell)
    integer(kind=iint), dimension(4), intent(in) :: cell
    integer(kind=iint) :: nli_destruct11

    select case(get_species(cell + (/0, -1, 0, PdO_hollow2/)))
      case(empty)
        select case(get_species(cell + (/0, -1, 0, PdO_bridge2/)))
          case(CO)
            select case(get_species(cell + (/0, 0, 0, PdO_hollow1/)))
              case(CO)
                select case(get_species(cell + (/0, 0, 0, PdO_bridge1/)))
                  case(CO)
                    nli_destruct11 = destruct11; return
                  case default
                    nli_destruct11 = 0; return
                end select
              case default
                nli_destruct11 = 0; return
            end select
          case default
            nli_destruct11 = 0; return
        end select
      case default
        nli_destruct11 = 0; return
    end select

end function nli_destruct11

end module
