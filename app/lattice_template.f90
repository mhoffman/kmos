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

%(unit_vector_definition)s
%(species_definition)s
%(lookup_table_init)s


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

    %(lookup_table_definition)s

    volume = system_size(2)*system_size(1)*%(sites_per_cell)s

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

%(lattice_mapping_functions)s

end module lattice
