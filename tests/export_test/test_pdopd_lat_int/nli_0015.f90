module nli_0015
use kind_values
use lattice
use proclist_constants
implicit none
contains
pure function nli_m_COads_b4(cell)
    integer(kind=iint), dimension(4), intent(in) :: cell
    integer(kind=iint) :: nli_m_COads_b4

    select case(get_species(cell + (/0, 0, 0, Pd100_b4/)))
      case(empty)
        nli_m_COads_b4 = m_COads_b4; return
      case default
        nli_m_COads_b4 = 0; return
    end select

end function nli_m_COads_b4

end module
