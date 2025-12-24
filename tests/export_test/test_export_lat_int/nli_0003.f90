module nli_0003
use kind_values
use lattice
use proclist_constants
implicit none
contains
pure function nli_co_desorption_cus(cell)
    integer(kind=iint), dimension(4), intent(in) :: cell
    integer(kind=iint) :: nli_co_desorption_cus

    select case(get_species(cell + (/0, 0, 0, ruo2_cus/)))
      case(co)
        nli_co_desorption_cus = co_desorption_cus; return
      case default
        nli_co_desorption_cus = 0; return
    end select

end function nli_co_desorption_cus

end module
