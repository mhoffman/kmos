#include "assert.ppc"
! Copyright (C)  2009 Max J. Hoffmann
!
! This file is part of libkmc.
!
! libkmc is free software; you can redistribute it and/or modify
! it under the terms of the GNU General Public License as published by
! the Free Software Foundation; either version 2 of the License, or
! (at your option) any later version.
!
! libkmc is distributed in the hope that it will be useful,
! but WITHOUT ANY WARRANTY; without even the implied warranty of
! MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
! GNU General Public License for more details.
!
! You should have received a copy of the GNU General Public License
! along with libkmc; if not, write to the Free Software
! Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301
! USA



module lattice
use kind_values
! Import and rename from libkmc
use libkmc, only: &
    assertion_fail, &
    deallocate_system, &
    get_kmc_step, &
    get_kmc_time, &
    get_kmc_time_step, &
    get_rate, &
    libkmc_increment_procstat => increment_procstat, &
    libkmc_add_proc => add_proc, &
    libkmc_allocate_system => allocate_system, &
    libkmc_can_do => can_do, &
    libkmc_del_proc => del_proc, &
    determine_procsite, &
    libkmc_replace_species => replace_species, &
    libkmc_get_species => get_species, &
    libkmc_get_volume  => get_volume, &
    libkmc_reload_system => reload_system, &
    null_species, &
    reload_system, &
    save_system, &
    set_rate, &
    update_accum_rate, &
    update_clocks

implicit none

private

! Public subroutines
public :: allocate_system, &
    null_species, &
    assertion_fail, &
    deallocate_system, &
    determine_procsite, &
    get_rate, &
    get_kmc_step, &
    get_kmc_time, &
    get_system_size, &
    increment_procstat, &
    reload_system, &
    save_system, &
    set_rate, &
    update_accum_rate, &
    %(lattice_name)s2nr, &
    nr2%(lattice_name)s, &
    %(lattice_name)s_increment_procstat, &
    %(lattice_name)s_add_proc, &
    %(lattice_name)s_can_do, &
    %(lattice_name)s_del_proc, &
    %(lattice_name)s_replace_species, &
    %(lattice_name)s_get_species, &
    update_clocks


type tuple
    integer(kind=iint), dimension(2) :: t
end type tuple

integer(kind=iint), dimension(2), public :: system_size

%(unit_vector_definition)s
%(species_definition)s
%(lookup_table_init)s


contains


subroutine %(lattice_name)s2nr(site, nr)
    !---------------I/O variables---------------
    integer(kind=iint), dimension(2), intent(in) :: site
    integer(kind=iint), intent(out) :: nr
    !---------------internal variables---------------
    integer(kind=iint) , dimension(2) :: folded_site, unit_cell, local_part
    integer(kind=iint) :: cell_nr

    ! Apply periodic boundary conditions
    folded_site = modulo(site, matmul(system_size, lattice_%(lattice_name)s_matrix))
    ! Determine unit cell
    unit_cell = site/(/lattice_%(lattice_name)s_matrix(1,1),lattice_%(lattice_name)s_matrix(2,2)/)
    ! Determine local part
    local_part = folded_site - matmul(lattice_%(lattice_name)s_matrix, unit_cell)
    ! Determine index of cell
    cell_nr = unit_cell(1) + system_size(1)*unit_cell(2)
    ! Put everything together
    nr = %(sites_per_cell)s*cell_nr + lookup_%(lattice_name)s2nr(local_part(1), local_part(2))


end subroutine %(lattice_name)s2nr


subroutine nr2%(lattice_name)s(nr, site)
    !---------------I/O variables---------------
    integer(kind=iint), intent(in) :: nr
    integer(kind=iint), dimension(2), intent(out) :: site
    !---------------internal variables---------------
    integer(kind=iint), dimension(2) :: cell, local_vector
    integer(kind=iint) :: local_nr, cell_nr

    ! Determine index of unit cell
    cell_nr = (nr - 1)/%(sites_per_cell)s
    ! Determine number within unit cell
    local_nr = modulo(nr, %(sites_per_cell)s)
    ! Determine unit cell
    cell(1) = modulo(cell_nr, system_size(1))
    cell(2) = cell_nr/system_size(1)
    ! Determine vector within unit cell
    local_vector = lookup_nr2%(lattice_name)s(local_nr)%%t
    ! Put everything together
    site = local_vector + matmul(lattice_%(lattice_name)s_matrix, cell)

end subroutine nr2%(lattice_name)s


subroutine get_system_size(return_system_size)
    !****f* lattice_%(lattice_name)s/get_system_size
    ! FUNCTION
    !    Simple wrapper subroutine to that return the system's dimensions
    !******
    !---------------I/O variables---------------
    integer(kind=iint), dimension(2), intent(out) :: return_system_size
    return_system_size = system_size

end subroutine get_system_size


subroutine allocate_system(nr_of_proc, input_system_size, system_name)
    !---------------I/O variables---------------
    !****f* lattice_%(lattice_name)s/allocate_system
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

    volume = system_size(2)*system_size(1)

    call libkmc_allocate_system(nr_of_proc, volume, system_name)

end subroutine allocate_system



subroutine %(lattice_name)s_add_proc(proc, site)
    !****f* lattice_%(lattice_name)s/%(lattice_name)s_add_proc
    ! FUNCTION
    !    The %(lattice_name)s version of core/add_proc
    !******
    !---------------I/O variables---------------
    integer(kind=iint), intent(in) :: proc
    integer(kind=iint), dimension(2), intent(in) :: site
    !---------------internal variables---------------
    integer(kind=iint) :: nr


    ! Convert %(lattice_name)s site to nr
    call %(lattice_name)s2nr(site, nr)

    ! Call likmc subroutine
    call libkmc_add_proc(proc, nr)

end subroutine %(lattice_name)s_add_proc


subroutine %(lattice_name)s_del_proc(proc, site)
    !****f* lattice_%(lattice_name)s/%(lattice_name)s_del_proc
    ! FUNCTION
    !    The %(lattice_name)s version of core/add_proc
    !******
    !---------------I/O variables---------------
    integer(kind=iint), intent(in) :: proc
    integer(kind=iint), dimension(2), intent(in) :: site
    !---------------internal variables---------------
    integer(kind=iint) :: nr

    ! Convert %(lattice_name)s site to nr
    call %(lattice_name)s2nr(site, nr)

    ! Call likmc subroutine
    call libkmc_del_proc(proc, nr)

end subroutine %(lattice_name)s_del_proc

subroutine %(lattice_name)s_can_do(proc, site, can)
    !---------------I/O variables---------------
    integer(kind=iint), intent(in) :: proc
    integer(kind=iint), dimension(2), intent(in) :: site
    logical, intent(out) :: can
    !---------------internal variables---------------
    integer(kind=iint) :: nr

    ! Convert %(lattice_name)s site to nr
    call %(lattice_name)s2nr(site, nr)

    ! Call likmc subroutine
    call libkmc_can_do(proc, nr, can)

end subroutine %(lattice_name)s_can_do


subroutine increment_procstat(proc)
    !---------------I/O variables---------------
    integer(kind=iint), intent(in) :: proc

    call libkmc_increment_procstat(proc)

end subroutine increment_procstat


subroutine %(lattice_name)s_increment_procstat(proc)
    !---------------I/O variables---------------
    integer(kind=iint), intent(in) :: proc

    call libkmc_increment_procstat(proc)

end subroutine %(lattice_name)s_increment_procstat


subroutine %(lattice_name)s_replace_species(site, old_species, new_species)
    !****f* lattice_%(lattice_name)s/%(lattice_name)s_replace_species
    ! FUNCTION
    !    The %(lattice_name)s version of core/replace_species
    !******
    !---------------I/O variables---------------
    integer(kind=iint), dimension(2), intent(in) :: site
    integer(kind=iint), intent(in) :: old_species, new_species
    !---------------internal variables---------------
    integer(kind=iint) :: nr

    ! Convert %(lattice_name)s site to nr
    call %(lattice_name)s2nr(site, nr)
    ! Call likmc subroutine
    call libkmc_replace_species(nr, old_species, new_species)

end subroutine %(lattice_name)s_replace_species


subroutine %(lattice_name)s_get_species(site, return_species)
    !****f* lattice_%(lattice_name)s/%(lattice_name)s_get_species
    ! FUNCTION
    !    The %(lattice_name)s  version of core/get_species
    !******
    !---------------I/O variables---------------
    integer(kind=iint), dimension(2), intent(in) :: site
    integer(kind=iint), intent(out) :: return_species
    !---------------internal variables---------------
    integer(kind=iint) :: nr

    ! Convert %(lattice_name)s site to nr
    call %(lattice_name)s2nr(site, nr)

    ! Call likmc subroutine
    call libkmc_get_species(nr, return_species)
end subroutine %(lattice_name)s_get_species


end module lattice
