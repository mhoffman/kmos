module nli_0017
use kind_values
use lattice
use proclist_constants
implicit none
contains
pure function nli_m_COdes_b6(cell)
    integer(kind=iint), dimension(4), intent(in) :: cell
    integer(kind=iint) :: nli_m_COdes_b6

    select case(get_species(cell + (/0, 0, 0, Pd100_b6/)))
      case(CO)
        nli_m_COdes_b6 = m_COdes_b6; return
      case default
        nli_m_COdes_b6 = 0; return
    end select

end function nli_m_COdes_b6

end module
