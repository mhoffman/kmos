module nli_0027
use kind_values
use lattice
use proclist_constants
implicit none
contains
pure function nli_m_COads_b5(cell)
    integer(kind=iint), dimension(4), intent(in) :: cell
    integer(kind=iint) :: nli_m_COads_b5

    select case(get_species(cell + (/0, 0, 0, Pd100_b5/)))
      case(empty)
        nli_m_COads_b5 = m_COads_b5; return
      case default
        nli_m_COads_b5 = 0; return
    end select

end function nli_m_COads_b5

end module
