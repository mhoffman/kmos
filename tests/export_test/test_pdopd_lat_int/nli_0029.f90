module nli_0029
use kind_values
use lattice
use proclist_constants
implicit none
contains
pure function nli_m_COads_b9(cell)
    integer(kind=iint), dimension(4), intent(in) :: cell
    integer(kind=iint) :: nli_m_COads_b9

    select case(get_species(cell + (/0, 0, 0, Pd100_b9/)))
      case(empty)
        nli_m_COads_b9 = m_COads_b9; return
      case default
        nli_m_COads_b9 = 0; return
    end select

end function nli_m_COads_b9

end module
