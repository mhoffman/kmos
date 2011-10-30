#!/usr/bin/env python
"""
Features front-end import/export functions for kMC Projects.
Currently import and export is supported to XML and export is
supported to Fortran 90 source code.
"""
#    Copyright 2009-2011 Max J. Hoffmann (mjhoffmann@gmail.com)
#    This file is part of kmos.
#
#    kmos is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    kmos is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with kmos.  If not, see <http://www.gnu.org/licenses/>.
import itertools
import operator
import shutil

from kmos.types import ConditionAction
from kmos.config import *


def _flatten(L):
    return [item for sublist in L for item in sublist]


def _most_common(L):
    # thanks go to Alex Martelli for this function
    # get an iterable of (item, iterable) pairs
    SL = sorted((x, i) for i, x in enumerate(L))
    # print 'SL:', SL
    groups = itertools.groupby(SL, key=operator.itemgetter(0))
    # auxiliary function to get "quality" for an item

    def _auxfun(g):
        item, iterable = g
        count = 0
        min_index = len(L)
        for _, where in iterable:
            count += 1
            min_index = min(min_index, where)
        # print 'item %r, count %r, minind %r' % (item, count, min_index)
        return count, -min_index
    # pick the highest-count/earliest item
    return max(groups, key=_auxfun)[0]


class ProcListWriter():
    """Write the different parts of Fortran 90 code needed
    to run a kMC model.
    """
    def __init__(self, data, dir):
        self.data = data
        self.dir = dir

    def write_lattice(self):
        """Write the lattice.f90 module, i.e. the geometric
        information that belongs to a kMC model.
        """
        # write header section and module imports
        data = self.data
        out = open(os.path.join(self.dir,'lattice.f90') , 'w')
        out.write(self._gpl_message())
        out.write('\n\nmodule lattice\n')
        out.write('use kind_values\n')
        out.write('use base, only: &\n')
        out.write('    assertion_fail, &\n')
        out.write('    base_deallocate_system => deallocate_system, &\n')
        out.write('    get_kmc_step, &\n')
        out.write('    get_kmc_time, &\n')
        out.write('    get_kmc_time_step, &\n')
        out.write('    get_rate, &\n')
        out.write('    increment_procstat, &\n')
        out.write('    base_add_proc => add_proc, &\n')
        out.write('    base_reset_site => reset_site, &\n')
        out.write('    base_allocate_system => allocate_system, &\n')
        out.write('    base_can_do => can_do, &\n')
        out.write('    base_del_proc => del_proc, &\n')
        out.write('    determine_procsite, &\n')
        out.write('    base_replace_species => replace_species, &\n')
        out.write('    base_get_species => get_species, &\n')
        out.write('    base_get_volume => get_volume, &\n')
        out.write('    reload_system => reload_system, &\n')
        out.write('    save_system, &\n')
        out.write('    assertion_fail, &\n')
        out.write('    null_species, &\n')
        out.write('    set_rate_const, &\n')
        out.write('    update_accum_rate, &\n')
        out.write('    update_clocks\n\n')

        out.write('\n\nimplicit none\n\n')

        # define module wide variables

        out.write('integer(kind=iint), dimension(3), public :: system_size\n')
        out.write('integer(kind=iint), parameter, public :: nr_of_layers = %s\n' % len(data.layer_list))
        out.write('\n ! Layer constants\n\n')
        out.write('integer(kind=iint), parameter, public :: model_dimension = %s\n' % (data.meta.model_dimension))
        for i, layer in enumerate(data.layer_list):
            out.write('integer(kind=iint), parameter, public :: %s = %s\n'
                % (layer.name, i))
        out.write('integer(kind=iint), parameter, public :: default_layer = %s\n' % data.layer_list.default_layer)
        out.write('integer(kind=iint), parameter, public :: substrate_layer = %s\n' % data.layer_list.substrate_layer)
        out.write('\n ! Site constants\n\n')
        site_params = self._get_site_params()
        out.write(('real(kind=rsingle), dimension(3,3), public :: unit_cell_size = 0.\n'))
        out.write('real(kind=rsingle), dimension(%s, 3), public :: site_positions\n' % len(site_params))
        for i, (site, layer, _) in enumerate(site_params):
            out.write(('integer(kind=iint), parameter, public :: %s_%s = %s\n')
                % (layer, site, i + 1))
        out.write('\n ! spuck = Sites Per Unit Cell Konstant\n')
        out.write('integer(kind=iint), parameter, public :: spuck = %s\n' % len(site_params))
        out.write(' ! lookup tables\n')
        out.write('integer(kind=iint), dimension(:, :), allocatable, public :: nr2lattice\n')
        out.write('integer(kind=iint), dimension(:,:,:,:), allocatable, public :: lattice2nr\n\n')
        out.write('\n\ncontains\n\n')

        # define the lattice mapping from the (multi-) lattice to a single lattice in 1D
        # and back. These mapping are the central piece of the lattice module and are used
        # by most of the other functions
        # For reasons of performance (modulo operation is usually considered expensive)
        # we write slightly different versions for d=1,2,3
        # where the lower dimension version simply ignore some fields
        out.write('pure function calculate_lattice2nr(site)\n\n')
        out.write('    integer(kind=iint), dimension(4), intent(in) :: site\n')
        out.write('    integer(kind=iint) :: calculate_lattice2nr\n\n')
        out.write('    ! site = (x,y,z,local_index)\n')

        if data.meta.model_dimension == 1:
            out.write('    calculate_lattice2nr = spuck*(modulo(site(1), system_size(1)))+site(4)')
        elif data.meta.model_dimension == 2:
            out.write('    calculate_lattice2nr = spuck*(&\n'
                + '      modulo(site(1), system_size(1))&\n'
                + '      + system_size(1)*modulo(site(2), system_size(2)))&\n'
                + '      + site(4)\n')
        elif data.meta.model_dimension == 3:
            out.write('    calculate_lattice2nr = spuck*(&\n'
                + '      modulo(site(1), system_size(1))&\n'
                + '      + system_size(1)*modulo(site(2), system_size(2))&\n'
                + '      + system_size(1)*system_size(2)*modulo(site(3), system_size(3)))&\n'
                + '      + site(4)\n')
        out.write('\nend function calculate_lattice2nr\n\n')

        out.write('pure function calculate_nr2lattice(nr)\n\n')
        out.write('    integer(kind=iint), intent(in) :: nr\n')
        out.write('    integer(kind=iint), dimension(4) :: calculate_nr2lattice\n\n')

        if data.meta.model_dimension == 3:
            out.write('    calculate_nr2lattice(3) = (nr - 1) /  (system_size(1)*system_size(2)*spuck)\n')
            out.write('    calculate_nr2lattice(2) = (nr - 1 - system_size(1)*system_size(2)*spuck*calculate_nr2lattice(3)) / (system_size(1)*spuck)\n')
            out.write('    calculate_nr2lattice(1) = (nr - 1 - spuck*(system_size(1)*system_size(2)*calculate_nr2lattice(3) &\n'
                + '        + system_size(1)*calculate_nr2lattice(2))) / spuck\n')
            out.write('    calculate_nr2lattice(4) = nr - spuck*(system_size(1)*system_size(2)*calculate_nr2lattice(3) + &\n'
                + '        system_size(2)*calculate_nr2lattice(2) + calculate_nr2lattice(1))\n')
        elif data.meta.model_dimension == 2:
            out.write('    calculate_nr2lattice(3) = 0\n')
            out.write('    calculate_nr2lattice(2) = (nr -1) / (system_size(1)*spuck)\n')
            out.write('    calculate_nr2lattice(1) = (nr - 1 - spuck*system_size(1)*calculate_nr2lattice(2)) / spuck\n')
            out.write('    calculate_nr2lattice(4) = nr - spuck*(system_size(1)*calculate_nr2lattice(2) + calculate_nr2lattice(1))\n')
        elif data.meta.model_dimension == 1:
            out.write('    calculate_nr2lattice(3) = 0\n')
            out.write('    calculate_nr2lattice(2) = 0\n')
            out.write('    calculate_nr2lattice(1) = (nr - 1) / spuck\n')
            out.write('    calculate_nr2lattice(4) = nr - spuck*calculate_nr2lattice(1)\n')
        out.write('\nend function calculate_nr2lattice\n\n')

        # allocate system replicates the base_allocate function
        # tests the lattice mappings for correctness
        # and initialized a lot more parameter type of data
        out.write('subroutine allocate_system(nr_of_proc, input_system_size, system_name)\n\n')
        out.write('    integer(kind=iint), intent(in) :: nr_of_proc\n')
        out.write('    integer(kind=iint), dimension(%s), intent(in) :: input_system_size\n' % data.meta.model_dimension)
        out.write('    character(len=200), intent(in) :: system_name\n\n')
        out.write('    integer(kind=iint) :: i, j, k, nr\n')
        out.write('    integer(kind=iint) :: check_nr\n')
        out.write('    integer(kind=iint) :: volume\n\n')
        out.write('    ! Copy to module wide variable\n')
        if data.meta.model_dimension == 3:
            out.write('    system_size = input_system_size\n')
        elif data.meta.model_dimension == 2:
            out.write('    system_size = (/input_system_size(1), input_system_size(2), 1/)\n')
        elif data.meta.model_dimension == 1:
            out.write('    system_size = (/input_system_size(1), 1, 1/)\n')

        out.write('    volume = system_size(1)*system_size(2)*system_size(3)*spuck\n')

        out.write('    ! Let\'s check if the works correctly, first\n')
        out.write('    ! and if so populate lookup tables\n')
        out.write('    do k = 0, system_size(3)-1\n')
        out.write('        do j = 0, system_size(2)-1\n')
        out.write('            do i = 0, system_size(1)-1\n')
        out.write('                do nr = 1, spuck\n')
        out.write('                    if(.not.all((/i,j,k,nr/).eq. &\n'
        + '                    calculate_nr2lattice(calculate_lattice2nr((/i,j,k,nr/)))))then\n')
        out.write('                        print *,"Error in Mapping:"\n')
        out.write('                        print *, (/i,j,k,nr/), "was mapped on", calculate_lattice2nr((/i,j,k,nr/))\n')
        out.write('                        print *, "but that was mapped on", calculate_nr2lattice(calculate_lattice2nr((/i,j,k,nr/)))\n')
        out.write('                        stop\n')
        out.write('                    endif\n')
        out.write('                end do\n')
        out.write('            end do\n')
        out.write('        end do\n')
        out.write('    end do\n\n')

        out.write('    do check_nr=1, product(system_size)*spuck\n')
        out.write('        if(.not.check_nr.eq.calculate_lattice2nr(calculate_nr2lattice(check_nr)))then\n')
        out.write('            print *, "ERROR in Mapping:", check_nr\n')
        out.write('            print *, "was mapped on", calculate_nr2lattice(check_nr)\n')
        out.write('            print *, "but that was mapped on",calculate_lattice2nr(calculate_nr2lattice(check_nr))\n')
        out.write('            stop\n')
        out.write('        endif\n')
        out.write('    end do\n\n')
        out.write('    allocate(nr2lattice(1:product(system_size)*spuck,4))\n')
        out.write('    allocate(lattice2nr(-system_size(1):2*system_size(1)-1, &\n'
            + '        -system_size(2):2*system_size(2)-1, &\n'
            + '        -system_size(3):2*system_size(3)-1, &\n'
            + '         1:spuck))\n')
        out.write('    do check_nr=1, product(system_size)*spuck\n')
        out.write('        nr2lattice(check_nr, :) = calculate_nr2lattice(check_nr)\n')
        out.write('    end do\n')
        out.write('    do k = -system_size(3), 2*system_size(3)-1\n')
        out.write('        do j = -system_size(2), 2*system_size(2)-1\n')
        out.write('            do i = -system_size(1), 2*system_size(1)-1\n')
        out.write('                do nr = 1, spuck\n')
        out.write('                    lattice2nr(i, j, k, nr) = calculate_lattice2nr((/i, j, k, nr/))\n')
        out.write('                end do\n')
        out.write('            end do\n')
        out.write('        end do\n')
        out.write('    end do\n\n')
        out.write('    call base_allocate_system(nr_of_proc, volume, system_name)\n\n')
        out.write('    unit_cell_size(1, 1) = %s\n' % data.layer_list.cell_size_x)
        out.write('    unit_cell_size(2, 2) = %s\n' % data.layer_list.cell_size_y)
        out.write('    unit_cell_size(3, 3) = %s\n' % data.layer_list.cell_size_z)
        for i, (_, _, (x, y, z)) in enumerate(site_params):
            out.write('    site_positions(%s,:) = (/%s, %s, %s/)\n' % (i + 1,
                                                                       float(x),
                                                                       float(y),
                                                                       float(z)))
        out.write('end subroutine allocate_system\n\n')

        # all subroutines below simply replicate the base module version
        # in terms of lattice coordinates. Could be stored in fixed template
        # but are kept here for completeness and readability

        out.write('subroutine deallocate_system()\n\n')
        out.write('    deallocate(lattice2nr)\n')
        out.write('    deallocate(nr2lattice)\n')
        out.write('    call base_deallocate_system()\n\n')
        out.write('end subroutine deallocate_system\n\n')

        out.write('subroutine add_proc(proc, site)\n\n')
        out.write('    integer(kind=iint), intent(in) :: proc\n')
        out.write('    integer(kind=iint), dimension(4), intent(in) :: site\n\n')
        out.write('    integer(kind=iint) :: nr\n\n')
        if data.meta.debug > 1:
            out.write('print *,"    LATTICE/ADD_PROC/PROC",proc\n')
            out.write('print *,"    LATTICE/ADD_PROC/SITE",site\n')
        out.write('    nr = lattice2nr(site(1), site(2), site(3), site(4))\n')
        out.write('    call base_add_proc(proc, nr)\n\n')
        out.write('end subroutine add_proc\n\n')

        out.write('subroutine del_proc(proc, site)\n\n')
        out.write('    integer(kind=iint), intent(in) :: proc\n')
        out.write('    integer(kind=iint), dimension(4), intent(in) :: site\n\n')
        out.write('    integer(kind=iint) :: nr\n\n')
        if data.meta.debug > 1:
            out.write('print *,"    LATTICE/DEL_PROC/PROC",proc\n')
            out.write('print *,"    LATTICE/DEL_PROC/SITE",site\n')
        out.write('    nr = lattice2nr(site(1), site(2), site(3), site(4))\n')
        out.write('    call base_del_proc(proc, nr)\n\n')
        out.write('end subroutine del_proc\n\n')

        out.write('pure function can_do(proc, site)\n\n')
        out.write('    logical :: can_do\n')
        out.write('    integer(kind=iint), intent(in) :: proc\n')
        out.write('    integer(kind=iint), dimension(4), intent(in) :: site\n\n')
        out.write('    integer(kind=iint) :: nr\n\n')
        out.write('    nr = lattice2nr(site(1), site(2), site(3), site(4))\n')
        out.write('    can_do = base_can_do(proc, nr)\n\n')
        out.write('end function can_do\n\n')

        out.write('subroutine replace_species(site,  old_species, new_species)\n\n')
        out.write('    integer(kind=iint), dimension(4), intent(in) ::site\n')
        out.write('    integer(kind=iint), intent(in) :: old_species, new_species\n\n')
        out.write('    integer(kind=iint) :: nr\n\n')
        out.write('    nr = lattice2nr(site(1), site(2), site(3), site(4))\n')
        out.write('    call base_replace_species(nr, old_species, new_species)\n\n')
        out.write('end subroutine replace_species\n\n')

        out.write('pure function get_species(site)\n\n')
        out.write('    integer(kind=iint) :: get_species\n')
        out.write('    integer(kind=iint), dimension(4), intent(in) :: site\n')
        out.write('    integer(kind=iint) :: nr\n\n')
        out.write('    nr = lattice2nr(site(1), site(2), site(3), site(4))\n')
        out.write('    get_species = base_get_species(nr)\n\n')
        out.write('end function get_species\n\n')

        out.write('subroutine reset_site(site, old_species)\n\n')
        out.write('    integer(kind=iint), dimension(4), intent(in) :: site\n')
        out.write('    integer(kind=iint), intent(in) :: old_species\n\n')
        out.write('    integer(kind=iint) :: nr\n\n')
        out.write('    nr = lattice2nr(site(1), site(2), site(3), site(4))\n')
        out.write('    call base_reset_site(nr, old_species)\n\n')
        out.write('end subroutine reset_site\n\n')

        out.write('end module lattice\n')
        out.close()

    def write_proclist(self):
        """Write the proclist.f90 module, i.e. the rules which make up
        the kMC process list.
        """
        # make long lines a little shorter
        data = self.data

        # write header section and module imports
        out = open('%s/proclist.f90' % self.dir, 'w')
        out.write(self._gpl_message())
        out.write('\n\nmodule proclist\n'
            + 'use kind_values\n'
            + 'use base, only: &\n'
            + '    update_accum_rate, &\n'
            + '    determine_procsite, &\n'
            + '    update_clocks, &\n'
            + '    increment_procstat\n\n')
        out.write('use lattice, only: &\n')
        site_params = []
        for layer in data.layer_list:
            out.write('    %s, &\n' % layer.name)
            for site in layer.sites:
                site_params.append((site.name, layer.name))
        for i, (site, layer) in enumerate(site_params):
            out.write(('    %s_%s, &\n') % (layer, site))
        out.write('    allocate_system, &\n'
            + '    nr2lattice, &\n'
            + '    lattice2nr, &\n'
            + '    add_proc, &\n'
            + '    can_do, &\n'
            + '    set_rate_const, &\n'
            + '    replace_species, &\n'
            + '    del_proc, &\n'
            + '    reset_site, &\n'
            + '    system_size, &\n'
            + '    spuck, &\n'
            + '    null_species, &\n'
            + '    get_species\n')
        out.write('\n\nimplicit none\n\n')

        # initialize various parameter kind of data
        out.write('\n\n ! Species constants\n\n')
        out.write('\n\ninteger(kind=iint), parameter, public :: nr_of_species = %s\n'\
            % (len(data.species_list)))
        for i, species in enumerate(sorted(data.species_list, key=lambda x: x.name)):
            out.write('integer(kind=iint), parameter, public :: %s = %s\n' % (species.name, i))
        out.write('integer(kind=iint), parameter, public :: default_species = %s\n' % (data.species_list.default_species))
        representation_length = max([len(species.representation) for species in data.species_list])

        out.write('integer(kind=iint), parameter, public :: representation_length = %s\n' % representation_length)

        out.write('\n\n! Process constants\n\n')
        for i, process in enumerate(self.data.process_list):
            out.write('integer(kind=iint), parameter, public :: %s = %s\n' % (process.name, i + 1))

        out.write('\n\ninteger(kind=iint), parameter, public :: nr_of_proc = %s\n'\
            % (len(data.process_list)))
        out.write('character(len=2000), dimension(%s) :: processes, rates' % (len(data.process_list)))
        out.write('\n\ncontains\n\n')

        # do exactly one kmc step
        out.write('subroutine do_kmc_step()\n\n')
        out.write('    real(kind=rsingle) :: ran_proc, ran_time, ran_site\n')
        out.write('    integer(kind=iint) :: nr_site, proc_nr\n\n')
        out.write('    call random_number(ran_time)\n')
        out.write('    call random_number(ran_proc)\n')
        out.write('    call random_number(ran_site)\n')
        if data.meta.debug > 0:
            out.write('print *,"PROCLIST/DO_KMC_STEP/RAN_TIME",ran_time\n')
            out.write('print *,"PROCLIST/DO_KMC_STEP/RAN_PROC",ran_proc\n')
            out.write('print *,"PROCLIST/DO_KMC_STEP/RAN_site",ran_site\n')
        out.write('    call update_accum_rate\n')
        out.write('    call determine_procsite(ran_proc, ran_time, proc_nr, nr_site)\n')
        if data.meta.debug > 0:
            out.write('print *,"PROCLIST/DO_KMC_STEP/PROC_NR", proc_nr\n')
        out.write('    call run_proc_nr(proc_nr, nr_site)\n')
        out.write('    call update_clocks(ran_time)\n\n')
        out.write('end subroutine do_kmc_step\n\n')

        out.write('subroutine get_occupation(occupation)\n\n')
        out.write('    ! nr_of_species = %s, spuck = %s\n' % (len(data.species_list), len(site_params)))
        out.write('    real(kind=rdouble), dimension(0:%s, 1:%s), intent(out) :: occupation\n\n' % (len(data.species_list) - 1, len(site_params)))
        out.write('    integer(kind=iint) :: i, j, k, nr, species\n\n')
        out.write('    occupation = 0\n\n')
        out.write('    do k = 0, system_size(3)-1\n')
        out.write('        do j = 0, system_size(2)-1\n')
        out.write('            do i = 0, system_size(1)-1\n')
        out.write('                do nr = 1, spuck\n')
        out.write('                    ! shift position by 1, so it can be accessed\n')
        out.write('                    ! more straightforwardly from f2py interface\n')
        out.write('                    species = get_species((/i,j,k,nr/))\n')
        out.write('                    if(species.gt.null_species) then\n')
        out.write('                    occupation(species, nr) = &\n')
        out.write('                        occupation(species, nr) + 1\n')
        out.write('                    endif\n')
        out.write('                end do\n')
        out.write('            end do\n')
        out.write('        end do\n')
        out.write('    end do\n\n')
        out.write('    occupation = occupation/real(system_size(1)*system_size(2)*system_size(3))\n')
        out.write('end subroutine get_occupation\n\n')
        # run_proc_nr runs the process selected by determine_procsite
        # for sake of simplicity each process is formulated in terms
        # of take and put operations. This is due to the fact that
        # in surface science type of models the default species,
        # i.e. 'empty' has a special meaning. So instead of just
        # 'setting' new species, which would be more general
        # we say we 'take' and 'put' atoms. So a take is equivalent
        # to a set_empty.
        # While this looks more readable on paper, I am not sure
        # if this make code maintainability a lot worse. So this
        # should probably change.

        out.write('subroutine run_proc_nr(proc, nr_site)\n\n')
        out.write('    integer(kind=iint), intent(in) :: proc\n')
        out.write('    integer(kind=iint), intent(in) :: nr_site\n\n')
        out.write('    integer(kind=iint), dimension(4) :: lsite\n\n')
        out.write('    call increment_procstat(proc)\n\n')
        out.write('    ! lsite = lattice_site, (vs. scalar site)\n')
        out.write('    lsite = nr2lattice(nr_site, :)\n\n')
        out.write('    select case(proc)\n')
        for process in data.process_list:
            out.write('    case(%s)\n' % process.name)
            if data.meta.debug > 0:
                out.write('print *,"PROCLIST/RUN_PROC_NR/NAME","%s"\n' % process.name)
                out.write('print *,"PROCLIST/RUN_PROC_NR/LSITE","lsite"\n')
                out.write('print *,"PROCLIST/RUN_PROC_NR/SITE","site"\n')
            for action in process.action_list:
                if action.coord == process.executing_coord():
                    relative_coord = 'lsite'
                else:
                    relative_coord = 'lsite%s' % (action.coord - process.executing_coord()).radd_ff()

                if action.species[0] == '^':
                    if data.meta.debug > 0:
                        out.write('print *,"PROCLIST/RUN_PROC_NR/ACTION","create %s_%s"\n' % (action.coord.layer, action.coord.name))
                    out.write('        call create_%s_%s(%s, %s)\n' % (action.coord.layer, action.coord.name, relative_coord, action.species[1:]))
                elif action.species[0] == '$':
                    if data.meta.debug > 0:
                        out.write('print *,"PROCLIST/RUN_PROC_NR/ACTION","annihilate %s_%s"\n' % (action.coord.layer, action.coord.name))
                    out.write('        call annihilate_%s_%s(%s, %s)\n' % (action.coord.layer, action.coord.name, relative_coord, action.species[1:]))
                elif action.species == data.species_list.default_species:
                    try:
                        previous_species = filter(lambda x: x.coord.ff() == action.coord.ff(), process.condition_list)[0].species
                    except:
                        UserWarning("Process %s seems to be ill-defined\n" % process.name)
                    if data.meta.debug > 0:
                        out.write('print *,"PROCLIST/RUN_PROC_NR/ACTION","take %s_%s %s"\n' % (action.coord.layer, action.coord.name, previous_species))
                    out.write('        call take_%s_%s_%s(%s)\n' % (previous_species, action.coord.layer, action.coord.name, relative_coord))
                else:
                    if data.meta.debug > 0:
                        out.write('print *,"PROCLIST/RUN_PROC_NR/ACTION","put %s_%s %s"\n' % (action.coord.layer, action.coord.name, action.species))
                    out.write('        call put_%s_%s_%s(%s)\n' % (action.species, action.coord.layer, action.coord.name, relative_coord))

            out.write('\n')
        out.write('    end select\n\n')
        out.write('end subroutine run_proc_nr\n\n')

        # Here we replicate the allocate_system call, initialize
        # all book-keeping databases
        # and calculate the rate constants for the first time
        out.write(('subroutine init(input_system_size, system_name, layer, species, no_banner)\n\n'
            + '    integer(kind=iint), intent(in) :: layer, species\n'
            + '    integer(kind=iint), dimension(%s), intent(in) :: input_system_size\n\n'
            + '    character(len=400), intent(in) :: system_name\n\n'
            + '    logical, optional, intent(in) :: no_banner\n\n'
            + '    if (.not. no_banner) then\n'
            + '        print *, "This kMC Model \'%s\' was written by %s (%s)"\n'
            + '        print *, "and implemented with the help of kmos,"\n'
            + '        print *, "which is distributed under"\n'
            + '        print *, "GNU/GPL Version 3 (C) Max J. Hoffmann mjhoffmann@gmail.com"\n'
            + '        print *, "kmos is in a very betaish stage and there is"\n'
            + '        print *, "ABSOLUTELY NO WARRANTY for correctness."\n'
            + '        print *, "Please check back with the author prior to using"\n'
            + '        print *, "results in a publication or presentation."\n\n'\
            + '    endif\n')
            % (data.meta.model_dimension, data.meta.model_name, data.meta.author, data.meta.email, ))
        if data.meta.debug > 0:
            out.write('print *,"PROCLIST/INIT/SYSTEM_SIZE",input_system_size\n')
        out.write('    call allocate_system(nr_of_proc, input_system_size, system_name)\n')
        out.write('    call initialize_state(layer, species)\n')
        out.write('end subroutine init\n\n')

        # initialize the system with the default layer and the default species
        # initialize all book-keeping databases
        # and representation strings for ASE representation
        out.write('subroutine initialize_state(layer, species)\n\n')
        out.write('    integer(kind=iint), intent(in) :: layer, species\n\n')
        out.write('    integer(kind=iint) :: i, j, k, nr\n')

        out.write('    do k = 0, system_size(3)-1\n')
        out.write('        do j = 0, system_size(2)-1\n')
        out.write('            do i = 0, system_size(1)-1\n')
        out.write('                do nr = 1, spuck\n')
        out.write('                    call reset_site((/i, j, k, nr/), null_species)\n')
        out.write('                end do\n')
        out.write('                select case(layer)\n')
        for layer in data.layer_list:
            out.write('                case (%s)\n' % layer.name)
            for site in layer.sites:
                out.write('                    call replace_species((/i, j, k, %s_%s/), null_species, %s)\n' % (layer.name, site.name, site.default_species))
        out.write('                end select\n')
        out.write('            end do\n')
        out.write('        end do\n')
        out.write('    end do\n\n')

        out.write('    do k = 0, system_size(3)-1\n')
        out.write('        do j = 0, system_size(2)-1\n')
        out.write('            do i = 0, system_size(1)-1\n')
        out.write('                select case(layer)\n')
        for layer in data.layer_list:
            out.write('                case(%s)\n' % layer.name)
            for site in layer.sites:
                out.write('                    call touchup_%s_%s((/i, j, k, %s_%s/))\n' % (2 * (layer.name, site.name)))
        out.write('                end select\n')
        out.write('            end do\n')
        out.write('        end do\n')
        out.write('    end do\n\n')

        out.write('\nend subroutine initialize_state\n\n')

        # HERE comes the bulk part of this code generator:
        # the put/take/create/annihilation functions
        # encode what all the processes we defined mean in terms
        # updates for the geometry and the list of available processes
        #
        # The updates that disable available process are pretty easy
        # and flat so they cannot be optimized much.
        # The updates enabling processes are more sophisticasted: most
        # processes have more than one condition. So enabling one condition
        # of a processes is not enough. We need to check if all the other
        # conditions are met after this update as well. All these checks
        # typically involve many repetitive questions, i.e. we will
        # inquire the lattice many times about the same site.
        # To mend this we first collect all processes that could be enabled
        # and then use a heuristic algorithm (any theoretical computer scientist
        # knows how to improve on this?) to construct an improved if-tree
        for species in data.species_list:
            if species.name == data.species_list.default_species:
                continue  # don't put/take 'empty'
            # iterate over all layers, sites, operations, process, and conditions ...
            for layer in data.layer_list:
                for site in layer.sites:
                    for op in ['put', 'take']:
                        enabled_procs = []
                        disabled_procs = []
                        # op = operation
                        routine_name = '%s_%s_%s_%s' % (op, species.name, layer.name, site.name)
                        out.write('subroutine %s(site)\n\n' % routine_name)
                        out.write('    integer(kind=iint), dimension(4), intent(in) :: site\n\n')
                        if data.meta.debug > 0:
                            out.write('print *,"PROCLIST/%s/SITE",site\n' % (routine_name.upper(), ))
                        out.write('    ! update lattice\n')
                        if op == 'put':
                            if data.meta.debug > 0:
                                out.write('print *,"    LATTICE/REPLACE_SPECIES/SITE",site\n')
                                out.write('print *,"    LATTICE/REPLACE_SPECIES/OLD_SPECIES","%s"\n' % data.species_list.default_species)
                                out.write('print *,"    LATTICE/REPLACE_SPECIES/NEW_SPECIES","%s"\n' % species.name)
                            out.write('    call replace_species(site, %s, %s)\n\n' % (data.species_list.default_species, species.name))
                        elif op == 'take':
                            if data.meta.debug > 0:
                                out.write('print *,"    LATTICE/REPLACE_SPECIES/SITE",site\n')
                                out.write('print *,"    LATTICE/REPLACE_SPECIES/OLD_SPECIES","%s"\n' % species.name)
                                out.write('print *,"    LATTICE/REPLACE_SPECIES/NEW_SPECIES","%s"\n' % data.species_list.default_species)
                            out.write('    call replace_species(site, %s, %s)\n\n' % (species.name, data.species_list.default_species))
                        for process in data.process_list:
                            for condition in process.condition_list:
                                if site.name == condition.coord.name and \
                                   layer.name == condition.coord.layer:
                                    # first let's check if we could be enabling any site
                                    # this can be the case if we put down a particle, and
                                    # it is the right one, or if we lift one up and the process
                                    # needs an empty site
                                    if op == 'put' \
                                        and  species.name == condition.species \
                                        or op == 'take' \
                                        and condition.species == data.species_list.default_species:

                                        # filter out the current condition, because we know we set it to true
                                        # right now
                                        other_conditions = filter(lambda x: x.coord != condition.coord, process.condition_list)
                                        # note how '-' operation is defined for Coord class !
                                        # we change the coordinate part to already point at
                                        # the right relative site
                                        other_conditions = [ConditionAction(
                                                species=other_condition.species,
                                                coord=('site%s' % (other_condition.coord - condition.coord).radd_ff())) for
                                                other_condition in other_conditions]
                                        enabled_procs.append((other_conditions, (process.name, 'site%s' % (process.executing_coord() - condition.coord).radd_ff(), True)))
                                    # and we disable something whenever we put something down, and the process
                                    # needs an empty site here or if we take something and the process needs
                                    # something else
                                    elif op == 'put' \
                                        and condition.species == data.species_list.default_species \
                                        or op == 'take' \
                                        and species.name == condition.species:
                                            coord = process.executing_coord() - condition.coord
                                            disabled_procs.append((process, coord))
                        # updating disabled procs is easy to do efficiently
                        # because we don't ask any questions twice, so we do it immediately
                        if disabled_procs:
                            out.write('    ! disable affected processes\n')
                            for process, coord in disabled_procs:
                                if data.meta.debug > 1:
                                    out.write('print *,"    LATTICE/CAN_DO/PROC",%s\n' % process.name)
                                    out.write('print *,"    LATTICE/CAN_DO/VSITE","site%s"\n' % (coord).radd_ff())
                                    out.write('print *,"    LATTICE/CAN_DO/SITE",site%s\n' % (coord).radd_ff())
                                out.write(('    if(can_do(%(proc)s, site%(coord)s))then\n'
                                + '        call del_proc(%(proc)s, site%(coord)s)\n'
                                + '    endif\n\n') % {'coord': (coord).radd_ff(), 'proc': process.name})

                        # updating enabled procs is not so simply, because meeting one condition
                        # is not enough. We need to know if all other conditions are met as well
                        # so we collect  all questions first and build a tree, where the most
                        # frequent questions are closer to the top
                        if enabled_procs:
                            out.write('    ! enable affected processes\n')

                            self._write_optimal_iftree(items=enabled_procs, indent=4, out=out)
                        out.write('\nend subroutine %s\n\n' % routine_name)

        for layer in data.layer_list:
            for site in layer.sites:
                routine_name = 'touchup_%s_%s' % (layer.name, site.name)
                out.write('subroutine %s(site)\n\n' % routine_name)
                out.write('    integer(kind=iint), dimension(4), intent(in) :: site\n\n')
                items = []
                for process in data.process_list:
                    executing_coord = process.executing_coord()
                    if executing_coord.layer == layer.name \
                        and executing_coord.name == site.name:
                        condition_list = [ConditionAction(
                            species=condition.species,
                            coord='site%s' % (condition.coord - executing_coord).radd_ff(),
                            ) for condition in process.condition_list]
                        items.append((condition_list, (process.name, 'site', True)))

                self._write_optimal_iftree(items=items, indent=4, out=out)
                out.write('end subroutine %s\n\n' % routine_name)

        if len(data.layer_list) > 1:
            # where are in multi-lattice mode
            for layer in data.layer_list:
                for site in layer.sites:
                    for special_op in ['create', 'annihilate']:
                        enabled_procs = []
                        disabled_procs = []
                        routine_name = '%s_%s_%s' % (special_op, layer.name, site.name)
                        out.write('subroutine %s(site, species)\n\n' % routine_name)
                        out.write('    integer(kind=iint), intent(in) :: species\n')
                        out.write('    integer(kind=iint), dimension(4), intent(in) :: site\n\n')
                        out.write('    ! update lattice\n')
                        if data.meta.debug > 0:
                            out.write('print *,"PROCLIST/%s/SITE",site\n' % (routine_name.upper(), ))
                        if special_op == 'create':
                            if data.meta.debug > 0:
                                out.write('print *,"    LATTICE/REPLACE_SPECIES/SITE",site\n')
                                out.write('print *,"    LATTICE/REPLACE_SPECIES/OLD_SPECIES","null_species"\n')
                                out.write('print *,"    LATTICE/REPLACE_SPECIES/NEW_SPECIES",species\n')
                            out.write('    call replace_species(site, null_species, species)\n\n')
                        elif special_op == 'annihilate':
                            if data.meta.debug > 0:
                                out.write('print *,"    LATTICE/REPLACE_SPECIES/SITE",site\n')
                                out.write('print *,"    LATTICE/REPLACE_SPECIES/OLD_SPECIES",species\n')
                                out.write('print *,"    LATTICE/REPLACE_SPECIES/NEW_SPECIES","null_species"\n')
                            out.write('    call replace_species(site, species, null_species)\n\n')

                        for process in data.process_list:
                            for condition in filter(lambda condition: condition.coord.name == site.name and
                                                                      condition.coord.layer == layer.name,
                                                                      process.condition_list):
                                if special_op == 'create':
                                    other_conditions = [ConditionAction(
                                            species=other_condition.species,
                                            coord=('site%s' % (other_condition.coord - condition.coord).radd_ff()))
                                            for other_condition in process.condition_list]
                                    enabled_procs.append((other_conditions, (process.name,
                                        'site%s' % (process.executing_coord()
                                        - condition.coord).radd_ff(), True)))
                                elif special_op == 'annihilate':
                                    coord = process.executing_coord() - condition.coord
                                    disabled_procs.append((process, coord))
                        if disabled_procs:
                            out.write('    ! disable affected processes\n')
                            for process, coord in disabled_procs:
                                if data.meta.debug > 1:
                                    out.write('print *,"    LATTICE/CAN_DO/PROC",%s\n' % process.name)
                                    out.write('print *,"    LATTICE/CAN_DO/VSITE","site%s"\n' % (coord).radd_ff())
                                    out.write('print *,"    LATTICE/CAN_DO/SITE",site%s\n' % (coord).radd_ff())
                                out.write(('    if(can_do(%(proc)s, site%(coord)s))then\n'
                                + '        call del_proc(%(proc)s, site%(coord)s)\n'
                                + '    endif\n\n') % {'coord': (coord).radd_ff(), 'proc': process.name})
                        if enabled_procs:
                            out.write('    ! enable affected processes\n')
                            self._write_optimal_iftree(items=enabled_procs, indent=4, out=out)
                        out.write('\nend subroutine %s\n\n' % routine_name)
        out.write('end module proclist\n')
        out.close()

    def _write_optimal_iftree(self, items, indent, out):
        # this function is called recursively
        # so first we define the ANCHORS or SPECIAL CASES
        # if no conditions are left, enable process immediately
        # I actually don't know if this tree is optimal
        # So consider this a heuristic solution which should give
        # on average better results than the brute force way

        # DEBUGGING
        #print(len(items))
        #print(items)
        for item in filter(lambda x: not x[0], items):
            # [1][2] field of the item determine if this search is intended for enabling (=True) or
            # disabling (=False) a process
            if item[1][2]:
                out.write('%scall add_proc(%s, %s)\n' % (' ' * indent, item[1][0], item[1][1]))
            else:
                out.write('%scall del_proc(%s, %s)\n' % (' ' * indent, item[1][0], item[1][1]))

        # and only keep those that have conditions
        items = filter(lambda x: x[0], items)
        if not items:
            return

        # DEBUGGING
        #print(len(items))
        #print(items)

        # now the GENERAL CASE
        # first find site, that is most sought after
        most_common_coord = _most_common([y.coord for y in _flatten([x[0] for x in items])])

        #DEBUGGING
        #print("MOST_COMMON_COORD: %s" % most_common_coord)

        # filter out list of uniq answers for this site
        answers = [y.species for y in filter(lambda x: x.coord == most_common_coord, _flatten([x[0] for x in items]))]
        uniq_answers = list(set(answers))

        #DEBUGGING
        #print("ANSWERS %s" % answers)
        #print("UNIQ_ANSWERS %s" % uniq_answers)

        if self.data.meta.debug > 1:
            out.write('print *,"    LATTICE/GET_SPECIES/VSITE","%s"\n' % most_common_coord)
            out.write('print *,"    LATTICE/GET_SPECIES/SITE",%s\n' % most_common_coord)
            out.write('print *,"    LATTICE/GET_SPECIES/SPECIES",get_species(%s)\n' % most_common_coord)

        out.write('%sselect case(get_species(%s))\n' % ((indent) * ' ', most_common_coord))
        for answer in uniq_answers:
            out.write('%scase(%s)\n' % ((indent) * ' ', answer))
            # this very crazy expression matches at items that contain
            # a question for the same coordinate and have the same answer here
            nested_items = filter(
                lambda x: (most_common_coord in [y.coord for y in x[0]]
                and answer == filter(lambda y: y.coord == most_common_coord, x[0])[0].species),
                items)
            # pruned items are almost identical to nested items, except the have
            # the one condition removed, that we just met
            pruned_items = []
            for nested_item in nested_items:
                conditions = filter(lambda x: most_common_coord != x.coord, nested_item[0])
                pruned_items.append((conditions, nested_item[1]))

            items = filter(lambda x: x not in nested_items, items)
            #print(len(nested_items))
            #print(nested_items)
            self._write_optimal_iftree(pruned_items, indent + 4, out)
        out.write('%send select\n\n' % (indent * ' ',))

        if items:
            # if items are left
            # the RECURSION II
            self._write_optimal_iftree(items, indent, out)

    def write_settings(self):
        """Write the kmc_settings.py. This contains all parameters, which
        can be changed on the fly and without recompilation of the Fortran 90
        modules.
        """

        from kmos import evaluate_rate_expression

        data = self.data
        out = open(os.path.join(self.dir,'kmc_settings.py'), 'w')
        out.write('model_name = \'%s\'\n' % self.data.meta.model_name)
        out.write('simulation_size = 20\n')
        out.write('representations = {\n')
        for species in sorted(data.species_list, key=lambda x: x.name):
            out.write('    "%s":"%s",\n'
                % (species.name,
                species.representation))
        out.write('    }\n\n')
        out.write('lattice_representation = "%s"\n\n' % data.layer_list.representation)
        site_params = self._get_site_params()
        out.write('site_names = %s\n' % ['%s_%s' % (x[1], x[0]) for x in site_params])

        out.write('parameters = {\n')
        for parameter in data.parameter_list:
            out.write(('    "%s":{"value":"%s", "adjustable":%s,'
            + ' "min":"%s", "max":"%s","scale":"%s"},\n') % (parameter.name,
                                          parameter.value,
                                          parameter.adjustable,
                                          parameter.min,
                                          parameter.max,
                                          parameter.scale))
        out.write('    }\n\n')
        out.write('rate_constants = {\n')
        for process in data.process_list:
            out.write('    "%s":("%s", %s),\n' % (process.name, process.rate_constant, process.enabled))
            try:
                parameters = {}
                for param in data.parameter_list:
                    parameters[param.name] = {'value': param.value}
                evaluate_rate_expression(process.rate_constant, parameters)
            except Exception, e:
                raise UserWarning('%s\nProcess: %s' % (e, process.name))

        out.write('    }\n\n')
        out.write('tof_count = {\n')
        print('len(process_list): %s' % len(data.process_list))
        for process in data.process_list:
            if process.tof_count is not None:
                out.write('    "%s":%s,\n' % (process.name, process.tof_count))
        out.write('    }\n\n')
        out.write('xml = """%s"""\n' % data)

        out.close()

    def _get_site_params(self):
        data = self.data
        site_params = []
        for layer in data.layer_list:
            for site in layer.sites:
                site_params.append((site.name, layer.name, (site.x, site.y, site.z)))
        return site_params

    def _gpl_message(self):
        """Prints the GPL statement at the top of the source file"""
        data = self.data
        out = ''
        out += "!  This file was generated by kMOS (kMC modelling on steroids)\n"
        out += "!  written by Max J. Hoffmann mjhoffmann@gmail.com (C) 2009-2011.\n"
        if hasattr(data.meta, 'author'):
            out += '!  The model was written by ' + data.meta.author + '.\n'
        out += """
!  This file is part of kmos.
!
!  kmos is free software; you can redistribute it and/or modify
!  it under the terms of the GNU General Public License as published by
!  the Free Software Foundation; either version 2 of the License, or
!  (at your option) any later version.
!
!  kmos is distributed in the hope that it will be useful,
!  but WITHOUT ANY WARRANTY; without even the implied warranty of
!  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
!  GNU General Public License for more details.
!
!  You should have received a copy of the GNU General Public License
!  along with kmos; if not, write to the Free Software
!  Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301
!  USA
"""
        return out


def export_source(project_tree, export_dir=None):
    """Export a kmos project into Fortran 90 code that can be readily
    compiled using f2py.  The model contained in project_tree
    will be stored under the directory export_dir. export_dir will
    be created if it does not exist. The XML representation of the
    model will be included in the kmc_settings.py module.
    """
    if export_dir is None:
        export_dir = project_tree.meta.model_name

    if not os.path.exists(export_dir):
        os.mkdir(export_dir)

    # copy files
    cp_files = [os.path.join('fortran_src', 'assert.ppc'),
                os.path.join('fortran_src', 'base.f90'),
                os.path.join('fortran_src', 'kind_values_f2py.f90'),
                os.path.join('fortran_src', 'run_kmc.f90')]
    exec_files = []

    for filename in cp_files + exec_files:
        shutil.copy(os.path.join(APP_ABS_PATH, filename), export_dir)
    for filename in exec_files:
        os.chmod(os.path.join(export_dir, filename), 0755)

    writer = ProcListWriter(project_tree, export_dir)
    writer.write_lattice()
    writer.write_proclist()
    writer.write_settings()
    project_tree.validate_model()
    return True

def import_xml(filename):
    """Imports and returns project from an XML file."""
    import kmos.types
    project_tree = kmos.types.ProjectTree()
    project_tree.import_xml_file(filename)
    return project_tree

def export_xml(project_tree, filename=None):
    """Writes a project to an XML file."""
    if filename is None:
        filename = '%s.xml' % project_tree.meta.model_name
    with open(filename, 'w') as f:
        for line in str(project_tree):
            f.write(line)
