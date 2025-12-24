module nli_0018
use kind_values
use lattice
use proclist_constants
implicit none
contains
pure function nli_m_COads_b7(cell)
    integer(kind=iint), dimension(4), intent(in) :: cell
    integer(kind=iint) :: nli_m_COads_b7

    select case(get_species(cell + (/0, 0, 0, Pd100_b7/)))
      case(empty)
        nli_m_COads_b7 = m_COads_b7; return
      case default
        nli_m_COads_b7 = 0; return
    end select

end function nli_m_COads_b7

end module
