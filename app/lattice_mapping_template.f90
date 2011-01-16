
subroutine %(lattice_name)s2nr(site, nr)
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
    nr = %(sites_per_cell)s*cell_nr + lookup_%(lattice_name)s2nr(local_part(1), local_part(2))



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


end subroutine %(lattice_name)s2nr


subroutine nr2%(lattice_name)s(nr, site)
    !---------------I/O variables---------------
    integer(kind=iint), intent(in) :: nr
    integer(kind=iint), dimension(2), intent(out) :: site
    !---------------internal variables---------------
    integer(kind=iint), dimension(2) :: cell, local_vector
    integer(kind=iint) :: local_nr, cell_nr

    ! Determine index of unit cell
    cell_nr = (nr-1)/%(sites_per_cell)s
    ! Determine number within unit cell
    local_nr = modulo(nr-1, %(sites_per_cell)s)+1
    ! Determine unit cell
    cell(1) = modulo(cell_nr, system_size(1))
    cell(2) = cell_nr/system_size(1)
    ! Determine vector within unit cell
    local_vector = lookup_nr2%(lattice_name)s(local_nr,:)
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

end subroutine nr2%(lattice_name)s



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
    call base_add_proc(proc, nr)

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
    call base_del_proc(proc, nr)

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
    call base_can_do(proc, nr, can)

end subroutine %(lattice_name)s_can_do


subroutine increment_procstat(proc)
    !---------------I/O variables---------------
    integer(kind=iint), intent(in) :: proc

    call base_increment_procstat(proc)

end subroutine increment_procstat


subroutine %(lattice_name)s_increment_procstat(proc)
    !---------------I/O variables---------------
    integer(kind=iint), intent(in) :: proc

    call base_increment_procstat(proc)

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
    call base_replace_species(nr, old_species, new_species)

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
    call base_get_species(nr, return_species)
end subroutine %(lattice_name)s_get_species
