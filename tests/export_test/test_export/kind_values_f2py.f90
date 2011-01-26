!/* ROBODOC this makes robodoc to document this file */
module kind_values
implicit none
!****h* kmos/kind_values(dummy)
! FUNCTION
!    note this file is a very evil duplication, which totally reverses the
!    idea of having platform independent kind values and a crutch. However
!    we need this as a workaround to remedy f2py's stupid non-working type
!    transformation
!******

integer, parameter :: rsingle = 4
integer, parameter :: rdouble = 4
integer, parameter :: ibyte = 1
integer, parameter :: ishort = 2
integer, parameter :: iint = 4
integer, parameter :: ilong =  8
end module kind_values
