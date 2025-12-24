module nli_0005
use kind_values
use lattice
use proclist_constants
implicit none
contains
pure function nli_co_diffusion_bridge_bridge_up(cell)
    integer(kind=iint), dimension(4), intent(in) :: cell
    integer(kind=iint) :: nli_co_diffusion_bridge_bridge_up

    select case(get_species(cell + (/0, 0, 0, ruo2_bridge/)))
      case(co)
        select case(get_species(cell + (/0, 1, 0, ruo2_bridge/)))
          case(empty)
            nli_co_diffusion_bridge_bridge_up = co_diffusion_bridge_bridge_up; return
          case default
            nli_co_diffusion_bridge_bridge_up = 0; return
        end select
      case default
        nli_co_diffusion_bridge_bridge_up = 0; return
    end select

end function nli_co_diffusion_bridge_bridge_up

end module
