module nli_0010
use kind_values
use lattice
use proclist_constants
implicit none
contains
pure function nli_co_diffusion_bridge_cus_right(cell)
    integer(kind=iint), dimension(4), intent(in) :: cell
    integer(kind=iint) :: nli_co_diffusion_bridge_cus_right

    select case(get_species(cell + (/0, 0, 0, ruo2_bridge/)))
      case(co)
        select case(get_species(cell + (/0, 0, 0, ruo2_cus/)))
          case(empty)
            nli_co_diffusion_bridge_cus_right = co_diffusion_bridge_cus_right; return
          case default
            nli_co_diffusion_bridge_cus_right = 0; return
        end select
      case default
        nli_co_diffusion_bridge_cus_right = 0; return
    end select

end function nli_co_diffusion_bridge_cus_right

end module
