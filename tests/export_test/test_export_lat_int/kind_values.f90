!/* ROBODOC this makes robodoc to document this file */
module kind_values
!****h* libkmc/kind_values
! FUNCTION
!    This module offers kind_values for commonly
!    used intrinsic types in a platform independent way.
!******
implicit none

integer, parameter :: rsingle = SELECTED_REAL_KIND(15, 200)
integer, parameter :: rdouble = SELECTED_REAL_KIND(15, 200)
integer, parameter :: ibyte = SELECTED_INT_KIND(2)
integer, parameter :: ishort = SELECTED_INT_KIND(4)
integer, parameter :: iint = SELECTED_INT_KIND(9)
integer, parameter :: ilong = SELECTED_INT_KIND(18)
end module kind_values
