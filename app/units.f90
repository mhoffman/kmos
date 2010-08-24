!/* ROBODOC this makes robodoc to document this file */
module units
!****h* libkmc/units
! FUNCTION
!    Several commonly used constants and conversion factors are offered
!    by this module, such a pi, the speed of light, the Planck constant,
!    the charge of an electron, k_Boltzmann, the atomic masses of carbon and oxygen,
!    the mass of a nucleon, one angstrom in meter, and one bar in Pascal.
!******

implicit none

real,parameter :: u_pi=3.14159265358979323846
real,parameter :: u_c=2.99792458e8  ! m/s
real,parameter :: u_h=6.62606876e-34 ! J s
real,parameter :: u_hbar=1.05457159642079e-34 ! J s
real,parameter :: u_e=1.602176462e-19 ! C
real,parameter :: u_kboltzmann=1.38065027755006e-23 ! J K
real,parameter :: u_carbon=12.011 ! atomic mass number
real,parameter :: u_oxygen=15.994  ! atomic mass number
real,parameter :: u_mass=1.66053873e-27 ! kg atomic mass
real,parameter :: u_angstrom=1E-10 ! m
real,parameter :: u_bar = 1E5 ! kg / m s^2

end module units
