program run_kmc
  
  use base
  use lattice
  use proclist

  integer :: i

  call init((/10,10,10/),'foobar', default_layer, default_species)
  do i = 1,1000000
    call do_kmc_step
  end do
end program run_kmc
