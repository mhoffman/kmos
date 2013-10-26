module nli_0043
use kind_values
use lattice
use proclist_constants
implicit none
contains
pure function nli_m_COdes_b10(cell)
    integer(kind=iint), dimension(4), intent(in) :: cell
    integer(kind=iint) :: nli_m_COdes_b10

    select case(get_species(cell + (/0, 0, 0, Pd100_b10/)))
      case(CO)
        nli_m_COdes_b10 = m_COdes_b10; return
      case default
        nli_m_COdes_b10 = 0; return
    end select

end function nli_m_COdes_b10

end module
