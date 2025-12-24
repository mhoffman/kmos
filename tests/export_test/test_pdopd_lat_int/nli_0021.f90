module nli_0021
use kind_values
use lattice
use proclist_constants
implicit none
contains
pure function nli_m_COdes_b1(cell)
    integer(kind=iint), dimension(4), intent(in) :: cell
    integer(kind=iint) :: nli_m_COdes_b1

    select case(get_species(cell + (/0, 0, 0, Pd100_b1/)))
      case(CO)
        nli_m_COdes_b1 = m_COdes_b1; return
      case default
        nli_m_COdes_b1 = 0; return
    end select

end function nli_m_COdes_b1

end module
