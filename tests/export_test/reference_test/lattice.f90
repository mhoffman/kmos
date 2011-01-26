#include "assert.ppc"
! Copyright (C)  2009 Max J. Hoffmann
!
! This file is part of kmos.
!
! kmos is free software; you can redistribute it and/or modify
! it under the terms of the GNU General Public License as published by
! the Free Software Foundation; either version 2 of the License, or
! (at your option) any later version.
!
! kmos is distributed in the hope that it will be useful,
! but WITHOUT ANY WARRANTY; without even the implied warranty of
! MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
! GNU General Public License for more details.
!
! You should have received a copy of the GNU General Public License
! along with kmos; if not, write to the Free Software
! Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301
! USA



module lattice
use kind_values
! Import and rename from base
use base, only: &
    assertion_fail, &
    deallocate_system, &
    get_kmc_step, &
    get_kmc_time, &
    get_kmc_time_step, &
    get_rate, &
    base_increment_procstat => increment_procstat, &
    base_add_proc => add_proc, &
    base_allocate_system => allocate_system, &
    base_can_do => can_do, &
    base_del_proc => del_proc, &
    determine_procsite, &
    base_replace_species => replace_species, &
    base_get_species => get_species, &
    base_get_volume  => get_volume, &
    base_reload_system => reload_system, &
    null_species, &
    reload_system, &
    save_system, &
    set_rate, &
    update_accum_rate, &
    update_clocks

implicit none




integer(kind=iint), dimension(2), public :: system_size

integer(kind=iint), dimension(2, 2) ::  lattice_matrix = reshape((/2, 0, 0, 1/), (/2, 2/))
integer(kind=iint), public, parameter :: &
    empty =  1, &
    oxygen =  2, &
    co = 3
character(len=800), dimension(3) :: species_list
integer(kind=iint), parameter :: nr_of_species = 3
integer(kind=iint), parameter :: nr_of_lattices = 1
character(len=800), dimension(1) :: lattice_list
integer(kind=iint), parameter, dimension(1) :: nr_of_sites = (/2/)
character(len=800), dimension(1, ruo2) :: site_list

integer(kind=iint), dimension(0:1, 0:0) :: lookup_ruo22nr
integer(kind=iint), dimension(1:2, 2) :: lookup_nr2ruo2



contains




subroutine get_system_size(return_system_size)
    !****f* lattice/get_system_size
    ! FUNCTION
    !    Simple wrapper subroutine to that return the system's dimensions
    !******
    !---------------I/O variables---------------
    integer(kind=iint), dimension(2), intent(out) :: return_system_size
    return_system_size = system_size

end subroutine get_system_size


subroutine allocate_system(nr_of_proc, input_system_size, system_name)
    !---------------I/O variables---------------
    !****f* lattice/allocate_system
    ! FUNCTION
    !    Allocates combined RuO_2 system.
    !    Replication of core/allocate_system
    ! ARGUMENTS
    !  * nr_of_proc -- integer value representing the total number of processes
    !  * input_system_size -- integer value representing the total number of sites
    !  * system_name -- string of 200 characters that determines the name of the reload
    !    file that will be saved as ./<system_name>.reload
    !******
    !---------------I/O variables---------------
    integer(kind=iint), intent(in) :: nr_of_proc
    integer(kind=iint), dimension(2), intent(in) :: input_system_size
    character(len=200), intent(in) :: system_name
    !---------------internal variables---------------
    integer(kind=iint) :: volume

    ! Copy to module wide variable
    system_size = input_system_size

    ! Fill lookup table nr2ruo2
    site_list(1) = "bridge"
    lookup_nr2ruo2(1, :) = (/0, 0/)
    site_list(2) = "cus"
    lookup_nr2ruo2(2, :) = (/1, 0/)


    ! Fill lookup table ruo22nr
    lookup_ruo22nr(0, 0) = 1
    lookup_ruo22nr(1, 0) = 2
    species_list(1) = "empty_ruo2"
    lattice_list(1) = "ruo2"
    species_list(2) = "oxygen_ruo2"
    lattice_list(2) = "ruo2"
    species_list(3) = "co_ruo2"
    lattice_list(3) = "ruo2"


    volume = system_size(2)*system_size(1)*2

    call base_allocate_system(nr_of_proc, volume, system_name)

end subroutine allocate_system




subroutine get_species_char(species_nr, char_slot, species_char)
    integer(kind=iint), intent(in) :: species_nr, char_slot
    character,  intent(out) :: species_char


    species_char = species_list(species_nr)(char_slot:char_slot)
end subroutine get_species_char

subroutine get_lattice_char(lattice_nr, char_slot, lattice_char)
    integer(kind=iint), intent(in) :: lattice_nr, char_slot
    character,  intent(out) :: lattice_char


    lattice_char = lattice_list(lattice_nr)(char_slot:char_slot)
end subroutine get_lattice_char

subroutine get_site_char(site_nr, char_slot, site_char)
    integer(kind=iint), intent(in) :: site_nr, char_slot
    character,  intent(out) :: site_char


    site_char = site_list(site_nr)(char_slot:char_slot)
end subroutine get_site_char


subroutine ruo22nr(site, nr)
    !---------------I/O variables---------------
    integer(kind=iint), dimension(2), intent(in) :: site
    integer(kind=iint), intent(out) :: nr
    !---------------internal variables---------------
    integer(kind=iint) , dimension(2) :: folded_site, unit_cell, local_part
    integer(kind=iint) :: cell_nr

    ! Apply periodic boundary conditions
    folded_site = modulo(site, matmul(system_size, lattice_matrix))
    ! Determine unit cell
    unit_cell = folded_site/(/lattice_matrix(1,1),lattice_matrix(2,2)/)
    ! Determine index of cell
    cell_nr = unit_cell(1) + system_size(1)*unit_cell(2)
    ! Determine local part
    local_part = folded_site - matmul(lattice_matrix, unit_cell)
    ! Put everything together
    nr = 2*cell_nr + lookup_ruo22nr(local_part(1), local_part(2))



    !! DEBUGGING
    !print *,'LATTICE TO NR-------------------------------',site
    !print *,'site',site
    !print *,'matmul(system_size, lattice_matrix)',matmul(system_size, lattice_matrix)
    !print *,'folded_site', folded_site
    !print *,'unit_cell',unit_cell
    !print *,'local_part',local_part
    !print *,'cell_nr',cell_nr
    !print *,'nr', nr
    !print *,'-------------------------------LATTICE TO NR'


end subroutine ruo22nr


subroutine nr2ruo2(nr, site)
    !---------------I/O variables---------------
    integer(kind=iint), intent(in) :: nr
    integer(kind=iint), dimension(2), intent(out) :: site
    !---------------internal variables---------------
    integer(kind=iint), dimension(2) :: cell, local_vector
    integer(kind=iint) :: local_nr, cell_nr

    ! Determine index of unit cell
    cell_nr = (nr-1)/2
    ! Determine number within unit cell
    local_nr = modulo(nr-1, 2)+1
    ! Determine unit cell
    cell(1) = modulo(cell_nr, system_size(1))
    cell(2) = cell_nr/system_size(1)
    ! Determine vector within unit cell
    local_vector = lookup_nr2ruo2(local_nr,:)
    ! Put everything together
    site = local_vector + matmul(lattice_matrix, cell)


    !! DEBUGGING
    !print *,'NR TO LATTICE---------------------------',nr
    !print *,'cell_nr',cell_nr
    !print *,'local_nr',local_nr
    !print *,'cell', cell
    !print *,'local_vector',local_vector
    !print *,'cell_nr',cell_nr
    !print *,'site', site
    !print *,'---------------------------NR TO LATTICE'

end subroutine nr2ruo2



subroutine ruo2_add_proc(proc, site)
    !****f* lattice_ruo2/ruo2_add_proc
    ! FUNCTION
    !    The ruo2 version of core/add_proc
    !******
    !---------------I/O variables---------------
    integer(kind=iint), intent(in) :: proc
    integer(kind=iint), dimension(2), intent(in) :: site
    !---------------internal variables---------------
    integer(kind=iint) :: nr


    ! Convert ruo2 site to nr
    call ruo22nr(site, nr)

    ! Call likmc subroutine
    call base_add_proc(proc, nr)

end subroutine ruo2_add_proc


subroutine ruo2_del_proc(proc, site)
    !****f* lattice_ruo2/ruo2_del_proc
    ! FUNCTION
    !    The ruo2 version of core/add_proc
    !******
    !---------------I/O variables---------------
    integer(kind=iint), intent(in) :: proc
    integer(kind=iint), dimension(2), intent(in) :: site
    !---------------internal variables---------------
    integer(kind=iint) :: nr

    ! Convert ruo2 site to nr
    call ruo22nr(site, nr)

    ! Call likmc subroutine
    call base_del_proc(proc, nr)

end subroutine ruo2_del_proc

subroutine ruo2_can_do(proc, site, can)
    !---------------I/O variables---------------
    integer(kind=iint), intent(in) :: proc
    integer(kind=iint), dimension(2), intent(in) :: site
    logical, intent(out) :: can
    !---------------internal variables---------------
    integer(kind=iint) :: nr

    ! Convert ruo2 site to nr
    call ruo22nr(site, nr)

    ! Call likmc subroutine
    call base_can_do(proc, nr, can)

end subroutine ruo2_can_do


subroutine increment_procstat(proc)
    !---------------I/O variables---------------
    integer(kind=iint), intent(in) :: proc

    call base_increment_procstat(proc)

end subroutine increment_procstat


subroutine ruo2_increment_procstat(proc)
    !---------------I/O variables---------------
    integer(kind=iint), intent(in) :: proc

    call base_increment_procstat(proc)

end subroutine ruo2_increment_procstat


subroutine ruo2_replace_species(site, old_species, new_species)
    !****f* lattice_ruo2/ruo2_replace_species
    ! FUNCTION
    !    The ruo2 version of core/replace_species
    !******
    !---------------I/O variables---------------
    integer(kind=iint), dimension(2), intent(in) :: site
    integer(kind=iint), intent(in) :: old_species, new_species
    !---------------internal variables---------------
    integer(kind=iint) :: nr

    ! Convert ruo2 site to nr
    call ruo22nr(site, nr)
    ! Call likmc subroutine
    call base_replace_species(nr, old_species, new_species)

end subroutine ruo2_replace_species


subroutine ruo2_get_species(site, return_species)
    !****f* lattice_ruo2/ruo2_get_species
    ! FUNCTION
    !    The ruo2  version of core/get_species
    !******
    !---------------I/O variables---------------
    integer(kind=iint), dimension(2), intent(in) :: site
    integer(kind=iint), intent(out) :: return_species
    !---------------internal variables---------------
    integer(kind=iint) :: nr

    ! Convert ruo2 site to nr
    call ruo22nr(site, nr)

    ! Call likmc subroutine
    call base_get_species(nr, return_species)
end subroutine ruo2_get_species


end module lattice
