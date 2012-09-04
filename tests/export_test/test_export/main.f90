program main

use kind_values, only: rdouble
use base, only: set_rate_const
use proclist, only : do_kmc_step, init, nr_of_proc
use lattice, only : deallocate_system, default_layer, model_dimension

character(400) :: sname = 'main'
integer, dimension(model_dimension) :: msize = 100
integer :: i
real(kind=rdouble) :: rate = 8000.

! initialize model
call init(msize, sname, default_layer, .true.)

! set rate constants
do i = 1, nr_of_proc
  call set_rate_const(i, rate)
enddo

! run some steps
do i = 1, 1000000
  call do_kmc_step()
enddo

! deallocate
call deallocate_system()

end program main
