!/* ROBODOC this makes robodoc to document this file */
module units
!****h* kmos/units
! FUNCTION
!    Several commonly used constants and conversion factors are offered
!    by this module, such a pi, the speed of light, the Planck constant,
!    the charge of an electron, k_Boltzmann, the atomic masses of carbon and oxygen,
!    the mass of a nucleon, one angstrom in meter, and one bar in Pascal.
!    Source: CODATA2010
!******

implicit none

real,parameter :: u_pi=3.14159265358979323846
real,parameter :: u_c=2.99792458e8  ! m/s
real,parameter :: u_h=6.62606957e-34 ! J s
real,parameter :: u_hbar=1.054571726e-34 ! J s
real,parameter :: u_e=1.602176565e-19 ! C
real,parameter :: u_kboltzmann=1.3806488e-23 ! J K
real,parameter :: u_umass=1.660538921e-27 ! kg atomic mass
real,parameter :: u_angstrom=1.E-10 ! m
real,parameter :: u_bar = 1.E5 ! kg / m s^2

end module units
