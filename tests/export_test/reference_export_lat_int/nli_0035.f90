module nli_0035
use kind_values
use lattice
use proclist_constants
implicit none
contains
pure function nli_co_adsorption_cus(cell)
    integer(kind=iint), dimension(4), intent(in) :: cell
    integer(kind=iint) :: nli_co_adsorption_cus

    select case(get_species(cell + (/0, 0, 0, ruo2_cus/)))
      case(empty)
        nli_co_adsorption_cus = co_adsorption_cus; return
      case default
        nli_co_adsorption_cus = 0; return
    end select

end function nli_co_adsorption_cus

end module
