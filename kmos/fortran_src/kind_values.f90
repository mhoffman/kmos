!/* ROBODOC this makes robodoc to document this file */
module kind_values
!****h* libkmc/kind_values
! FUNCTION
!    This module offers kind_values for commonly
!    used intrinsic types in a platform independent way.
!******
implicit none

integer, parameter :: rsingle = SELECTED_REAL_KIND(p=15, r=200)
integer, parameter :: rdouble = SELECTED_REAL_KIND(p=15, r=200)
integer, parameter :: ibyte = SELECTED_INT_KIND(p=2)
integer, parameter :: ishort = SELECTED_INT_KIND(p=4)
integer, parameter :: iint = SELECTED_INT_KIND(p=9)
integer, parameter :: ilong = SELECTED_INT_KIND(p=18)
end module kind_values
