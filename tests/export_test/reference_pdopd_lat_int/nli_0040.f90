module nli_0040
use kind_values
use lattice
use proclist_constants
implicit none
contains
pure function nli_oxidize1(cell)
    integer(kind=iint), dimension(4), intent(in) :: cell
    integer(kind=iint) :: nli_oxidize1

    select case(get_species(cell + (/0, -1, 0, Pd100_b10/)))
      case(empty)
        select case(get_species(cell + (/0, -1, 0, Pd100_b7/)))
          case(empty)
            select case(get_species(cell + (/0, 0, 0, Pd100_h1/)))
              case(oxygen)
                select case(get_species(cell + (/0, 0, 0, Pd100_b1/)))
                  case(empty)
                    select case(get_species(cell + (/0, 0, 0, Pd100_b9/)))
                      case(empty)
                        nli_oxidize1 = oxidize1; return
                      case default
                        nli_oxidize1 = 0; return
                    end select
                  case default
                    nli_oxidize1 = 0; return
                end select
              case default
                nli_oxidize1 = 0; return
            end select
          case default
            nli_oxidize1 = 0; return
        end select
      case default
        nli_oxidize1 = 0; return
    end select

end function nli_oxidize1

end module
